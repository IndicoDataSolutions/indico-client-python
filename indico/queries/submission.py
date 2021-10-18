import json
import time
from functools import partial
from operator import eq, ne
from typing import Dict, List, Union

from indico.client.request import GraphQLRequest, RequestChain
from indico.errors import IndicoInputError, IndicoTimeoutError
from indico.filters import SubmissionFilter
from indico.queries import JobStatus
from indico.types import Job, Submission
from indico.types.submission import VALID_SUBMISSION_STATUSES


class ListSubmissions(GraphQLRequest):
    """
    List all Submissions visible to the authenticated user by most recent.

    Options:
        submission_ids (List[int]): Submission ids to filter by
        workflow_ids (List[int]): Workflow ids to filter by
        filters (SubmissionFilter or Dict): Submission attributes to filter by
        limit (int, default=1000): Maximum number of Submissions to return
        orderBy (str, default="ID"): Submission attribute to filter by
        desc: (bool, default=True): List in descending order

    Returns:
        List[Submission]: All the found Submission objects
    """

    query = """
        query ListSubmissions(
            $submissionIds: [Int],
            $workflowIds: [Int],
            $filters: SubmissionFilter,
            $limit: Int,
            $orderBy: SUBMISSION_COLUMN_ENUM,
            $desc: Boolean

        ){
            submissions(
                submissionIds: $submissionIds,
                workflowIds: $workflowIds,
                filters: $filters,
                limit: $limit
                orderBy: $orderBy,
                desc: $desc

            ){
                submissions {
                    id
                    datasetId
                    workflowId
                    status
                    inputFile
                    inputFilename
                    resultFile
                    deleted
                    retrieved
                    errors
                }
            }
        }
    """

    def __init__(
        self,
        *,
        submission_ids: List[int] = None,
        workflow_ids: List[int] = None,
        filters: Union[Dict, SubmissionFilter] = None,
        limit: int = 1000,
        order_by: str = "ID",
        desc: bool = True,
    ):
        super().__init__(
            self.query,
            variables={
                "submissionIds": submission_ids,
                "workflowIds": workflow_ids,
                "filters": filters,
                "limit": limit,
                "orderBy": order_by,
                "desc": desc,
            },
        )

    def process_response(self, response) -> List[Submission]:
        return [
            Submission(**s)
            for s in super().process_response(response)["submissions"]["submissions"]
        ]


class GetSubmission(GraphQLRequest):
    """
    Retrieve a Submission by id

    Args:
        submission_id (int): Submission id

    Returns:
        Submission: Found Submission object
    """

    query = """
        query GetSubmission($submissionId: Int!){
            submission(id: $submissionId){
                id
                datasetId
                workflowId
                status
                inputFile
                inputFilename
                resultFile
                retrieved
                deleted
                errors
            }
        }
    """

    def __init__(self, submission_id: int):
        super().__init__(self.query, variables={"submissionId": submission_id})

    def process_response(self, response) -> Submission:
        return Submission(**(super().process_response(response)["submission"]))


class WaitForSubmissions(RequestChain):
    """
    Given submission_ids, wait for all to finish processing
    """

    query = """
        query ListSubmissions(
            $submissionIds: [Int],
        ){
            submissions(
                submissionIds: $submissionIds,
            ){
                submissions {
                    id
                    datasetId
                    workflowId
                    status
                    inputFile
                    inputFilename
                    resultFile
                    retrieved
                    deleted
                    errors
                }
            }
        }
    """

    def __init__(self, submission_ids: List[int], timeout: Union[int, float] = 60):
        if not submission_ids:
            raise IndicoInputError("Please provide submission ids")

        self.submission_ids = submission_ids
        self.timeout = timeout
        self.status_check = partial(ne, "PROCESSING")
        self.status_getter = partial(
            ListSubmissions, submission_ids=self.submission_ids, limit=None
        )

    def requests(self) -> List[Submission]:
        yield self.status_getter()
        curr_time = 0
        while (
            not all(self.status_check(s.status) for s in self.previous)
            and curr_time <= self.timeout
        ):
            yield self.status_getter()
            time.sleep(1)
            curr_time += 1
        if not all(self.status_check(s.status) for s in self.previous):
            raise IndicoTimeoutError(curr_time)


class UpdateSubmission(GraphQLRequest):
    """
    Update the retrieval status of a Submission by id

    Args:
        submission_id (int): Submission id
        retrieved (bool): Bool to indicate if you have retrieved prediction results

    Returns:
        Submission: Found Submission object
    """

    query = """
        mutation UpdateSubmission($submissionId: Int!, $retrieved: Boolean) {
            updateSubmission(submissionId: $submissionId, retrieved: $retrieved) {
                id
                datasetId
                workflowId
                status
                inputFile
                inputFilename
                resultFile
                retrieved
                deleted
                errors
            }
        }
    """

    def __init__(self, submission_id: int, retrieved: bool):
        """
        Update properties of the Submission object

        Args:
            submission_id (int): Id of the submission to update
            retrieved (bool): Mark the submission as having been retrieved

        Returns:
            Submission: The updated Submission object
        """
        super().__init__(
            self.query,
            variables={"submissionId": submission_id, "retrieved": retrieved},
        )

    def process_response(self, response) -> Submission:
        return Submission(**(super().process_response(response)["updateSubmission"]))


class GenerateSubmissionResult(GraphQLRequest):
    query = """
        mutation CreateSubmissionResults($submissionId: Int!) {
            submissionResults(submissionId: $submissionId) {
                jobId
            }
        }

    """

    def __init__(self, submission: Union[int, Submission]):
        submission_id = submission if isinstance(submission, int) else submission.id
        super().__init__(self.query, variables={"submissionId": submission_id})

    def process_response(self, response) -> Job:
        response = super().process_response(response)["submissionResults"]
        return Job(id=response["jobId"])


class SubmissionResult(RequestChain):
    """
    Generate a result file for a Submission

    Args:
        submission (int or Submission): Id of the submission or Submission object
        check_status (str, optional): Submission status to check for.
            Defaults to any status other than `PROCESSING`
        wait (bool, optional): Wait until the submission is `check_status`
            and wait for the result file to be generated. Defaults to False
        timeout (int or float, optional): Maximum number of seconds to wait before
            timing out. Ignored if not `wait`. Defaults to 30

    Returns:
        Job: A Job that can be watched for results

    Raises:
        if `wait`:
            IndicoTimeoutError: Submission was not `check_status`
               `or result file Job did not complete within `timeout` seconds.
        If not `wait`:
            IndicoInputError: The requested Submission is not `check_status`
    """

    previous: Submission = None

    def __init__(
        self,
        submission: Union[int, Submission],
        check_status: str = None,
        wait: bool = False,
        timeout: Union[int, float] = 30,
    ):
        self.submission_id = (
            submission if isinstance(submission, int) else submission.id
        )
        self.wait = wait
        self.timeout = timeout
        if check_status and check_status.upper() not in VALID_SUBMISSION_STATUSES:
            raise IndicoInputError(
                f"{check_status} is not one of valid submission statuses: "
                f"{VALID_SUBMISSION_STATUSES}"
            )
        self.status_check = (
            partial(eq, check_status.upper())
            if check_status
            else partial(ne, "PROCESSING")
        )

    def requests(self) -> Union[Job, str]:
        yield GetSubmission(self.submission_id)
        if self.wait:
            curr_time = 0
            while (
                not self.status_check(self.previous.status)
                and curr_time <= self.timeout
            ):
                yield GetSubmission(self.submission_id)
                time.sleep(1)
                curr_time += 1
            if not self.status_check(self.previous.status):
                raise IndicoTimeoutError(curr_time)
        elif not self.status_check(self.previous.status):
            raise IndicoInputError(
                f"Submission {self.submission_id} does not meet status requirements"
            )

        yield GenerateSubmissionResult(self.submission_id)
        if self.wait:
            yield JobStatus(id=self.previous.id, wait=True, timeout=self.timeout)


class SubmitReview(GraphQLRequest):
    """
    Submit an "Auto" Review for a submission. Requires that the submission be in PENDING_AUTO_REVIEW status.

    Args:
        submission_id (int): Id of submission to submit reviewEnabled for

    Options:
        changes (dict or JSONString): changes to make to raw predictions

        rejected (boolean): reject the predictions and place the submission
            in the review queue. Must be True if $changes not provided

        force_complete (boolean): have this submission bypass the Review queue
            (or exceptions queue if <rejected> is True) and mark as Complete.
            NOT RECOMMENDED

    Returns:
        Job: A Job that can be watched for status of review
    """

    query = """
        mutation SubmitReview(<QUERY ARGS>) {
            submitAutoReview(<AUTO REVIEW ARGS>) {
                jobId
            }
        }

    """
    query_args = {
        "submissionId": "Int!",
        "changes": "JSONString",
        "rejected": "Boolean",
    }

    def __init__(
        self,
        submission: Union[int, Submission],
        changes: Dict = None,
        rejected: bool = False,
        force_complete: bool = None,
    ):
        submission_id = submission if isinstance(submission, int) else submission.id
        if not changes and not rejected:
            raise IndicoInputError("Must provide changes or reject=True")
        elif changes and isinstance(changes, dict):
            changes = json.dumps(changes)
        _vars = {
            "submissionId": submission_id,
            "changes": changes,
            "rejected": rejected,
        }

        # Add backwards-incompatible args now
        if force_complete is not None:
            _vars["forceComplete"] = force_complete
            self.query_args["forceComplete"] = "Boolean"

        query = self.query.replace(
            "<QUERY ARGS>", ",".join(f"${k}: {v}" for k, v in self.query_args.items())
        )
        query = query.replace(
            "<AUTO REVIEW ARGS>", ",".join(f"{k}: ${k}" for k in self.query_args)
        )

        super().__init__(query, variables=_vars)

    def process_response(self, response) -> Job:
        response = super().process_response(response)["submitAutoReview"]
        return Job(id=response["jobId"])


class RetrySubmission(GraphQLRequest):
    """
    Given a list of submission ids, retry those failed submissions.

    Attributes:
        submission_ids (List[int]): the given submission ids to retry.
    """

    query = """
    mutation retrySubmission($submissionIds:[Int]!){
  retrySubmissions(submissionIds: $submissionIds){
    status
    id
    errors
    retries{
      id
      previousErrors
      previousStatus
      retryErrors
      submissionId
    }
  }
}
    """

    def __init__(self, submission_ids: List[int]):
        if submission_ids is None or len(submission_ids) < 1:
            raise IndicoInputError("You must specify submission ids")

        super().__init__(self.query, variables={"submissionIds": submission_ids})

    def process_response(self, response) -> List[Submission]:
        return [
            Submission(**s)
            for s in super().process_response(response)["retrySubmissions"]
        ]
