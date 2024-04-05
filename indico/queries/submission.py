import json
from functools import partial
from operator import eq, ne
from typing import TYPE_CHECKING

from indico.client.request import Delay, GraphQLRequest, PagedRequest, RequestChain
from indico.errors import IndicoInputError, IndicoTimeoutError
from indico.filters import SubmissionFilter
from indico.queries import JobStatus
from indico.types import Job, Submission, SubmissionReviewFull
from indico.types.submission import VALID_SUBMISSION_STATUSES
from indico.types.utils import Timer

if TYPE_CHECKING:  # pragma: no cover
    from typing import Iterator, List, Optional, Union

    from indico.typing import AnyDict, Payload


class ListSubmissions(PagedRequest["List[Submission]"]):
    """
    List all Submissions visible to the authenticated user by most recent.
    Supports pagination (limit becomes page_size)

    Options:
        submission_ids (List[int]): Submission ids to filter by
        workflow_ids (List[int]): Workflow ids to filter by
        filters (SubmissionFilter or Dict): Submission attributes to filter by
        limit (int, default=1000): Maximum number of Submissions to return
        orderBy (str, default="ID"): Submission attribute to filter by
        desc: (bool, default=True): List in descending order

    Returns:
        List[Submission]: All the found Submission objects
        If paginated, yields results one at a time
    """

    query = """
        query ListSubmissions(
            $submissionIds: [Int]
            $workflowIds: [Int]
            $filters: SubmissionFilter
            $limit: Int
            $orderBy: SUBMISSION_COLUMN_ENUM
            $desc: Boolean
            $after: Int
            ) {
            submissions(
                submissionIds: $submissionIds
                workflowIds: $workflowIds
                filters: $filters
                limit: $limit
                orderBy: $orderBy
                desc: $desc
                after: $after
            ) {
                submissions {
                id
                datasetId
                workflowId
                status
                createdAt
                updatedAt
                createdBy
                updatedBy
                completedAt
                errors
                filesDeleted
                inputFiles {
                    id
                    filepath
                    filename
                    filetype
                    submissionId
                    fileSize
                    numPages
                }
                inputFile
                inputFilename
                resultFile
                outputFiles {
                    id
                    filepath
                    submissionId
                    componentId
                    createdAt
                }
                retrieved
                autoReview {
                    id
                    submissionId
                    createdAt
                    createdBy
                    startedAt
                    completedAt
                    rejected
                    reviewType
                    notes
                }
                retries {
                    id
                    submissionId
                    previousErrors
                    previousStatus
                    retryErrors
                }
                reviews {
                    id
                    submissionId
                    createdAt
                    createdBy
                    startedAt
                    completedAt
                    rejected
                    reviewType
                    notes
                }
                reviewInProgress
                }
                pageInfo {
                startCursor
                endCursor
                hasNextPage
                aggregateCount
                }
            }
        }
    """

    def __init__(
        self,
        *,
        submission_ids: "Optional[List[int]]" = None,
        workflow_ids: "Optional[List[int]]" = None,
        filters: "Optional[Union[AnyDict, SubmissionFilter]]" = None,
        limit: "Optional[int]" = 1000,
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

    def process_response(self, response: "Payload") -> "List[Submission]":
        return [
            Submission(**s)
            for s in super().parse_payload(response)["submissions"]["submissions"]
        ]


class GetSubmission(GraphQLRequest["Submission"]):
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
                createdAt
                updatedAt
                createdBy
                updatedBy
                completedAt
                errors
                filesDeleted
                inputFiles {
                    id
                    filepath
                    filename
                    filetype
                    submissionId
                    fileSize
                    numPages
                }
                inputFile
                inputFilename
                resultFile
                outputFiles {
                    id
                    filepath
                    submissionId
                    componentId
                    createdAt
                }
                retrieved
                autoReview {
                    id
                    submissionId
                    createdAt
                    createdBy
                    startedAt
                    completedAt
                    rejected
                    reviewType
                    notes
                }
                retries {
                    id
                    submissionId
                    previousErrors
                    previousStatus
                    retryErrors
                }
                reviews {
                    id
                    submissionId
                    createdAt
                    createdBy
                    startedAt
                    completedAt
                    rejected
                    reviewType
                    notes
                }
                reviewInProgress
            }
        }
    """

    def __init__(self, submission_id: int):
        super().__init__(self.query, variables={"submissionId": submission_id})

    def process_response(self, response: "Payload") -> "Submission":
        return Submission(**(super().parse_payload(response)["submission"]))


class WaitForSubmissions(RequestChain["List[Submission]"]):
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
                    inputFiles {
                        id
                        filename
                        filepath
                        filetype
                        fileSize
                        numPages
                    }
                    inputFile
                    inputFilename
                    resultFile
                    retrieved
                    filesDeleted
                    errors
                    reviews {
                        id
                        createdAt
                        createdBy
                        completedAt
                        rejected
                        reviewType
                        notes
                    }
                }
            }
        }
    """

    def __init__(self, submission_ids: "List[int]", timeout: "Union[int, float]" = 60):
        if not submission_ids:
            raise IndicoInputError("Please provide submission ids")

        self.submission_ids = submission_ids
        self.timeout = timeout
        self.status_check = partial(ne, "PROCESSING")
        self.status_getter = partial(
            ListSubmissions, submission_ids=self.submission_ids, limit=None
        )

    def requests(self) -> "Iterator[ListSubmissions]":
        timer = Timer(self.timeout)

        while True:
            timer.check()
            yield self.status_getter()
            if all(self.status_check(s.status) for s in self.previous):
                break


class UpdateSubmission(GraphQLRequest["Submission"]):
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
                inputFiles {
                    id
                    filename
                    filepath
                    filetype
                    fileSize
                    numPages
                }
                inputFile
                inputFilename
                resultFile
                retrieved
                filesDeleted
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

    def process_response(self, response: "Payload") -> "Submission":
        return Submission(**(super().parse_payload(response)["updateSubmission"]))


class GenerateSubmissionResult(GraphQLRequest["Job"]):
    query = """
        mutation CreateSubmissionResults($submissionId: Int!) {
            submissionResults(submissionId: $submissionId) {
                jobId
            }
        }

    """

    def __init__(self, submission: "Union[int, Submission]"):
        submission_id = submission if isinstance(submission, int) else submission.id
        super().__init__(self.query, variables={"submissionId": submission_id})

    def process_response(self, response: "Payload") -> "Job":
        response = super().parse_payload(response)["submissionResults"]
        return Job(id=response["jobId"])


class SubmissionResult(RequestChain["Job"]):
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
        request_interval (int or float, optional): The maximum time in between retry calls when waiting. Defaults to 5 seconds.

    Returns:
        Job: A Job that can be watched for results

    Raises:
        if `wait`:
            IndicoTimeoutError: Submission was not `check_status`
               `or result file Job did not complete within `timeout` seconds.
        If not `wait`:
            IndicoInputError: The requested Submission is not `check_status`
    """

    def __init__(
        self,
        submission: "Union[int, Submission]",
        check_status: "Optional[str]" = None,
        wait: bool = False,
        timeout: "Union[int, float]" = 30,
        request_interval: "Union[int, float]" = 5,
    ):
        self.submission_id = (
            submission if isinstance(submission, int) else submission.id
        )
        self.wait = wait
        self.timeout = timeout
        self.request_interval = request_interval
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

    def requests(
        self,
    ) -> "Iterator[Union[GetSubmission, Delay, GenerateSubmissionResult, JobStatus]]":
        timer = Timer(self.timeout)
        timer.check()
        yield GetSubmission(self.submission_id)
        if self.wait:
            while not self.status_check(self.previous.status):
                timer.check()
                yield GetSubmission(self.submission_id)
                yield Delay(seconds=self.request_interval)
            if not self.status_check(self.previous.status):
                raise IndicoTimeoutError(timer.elapsed)
        elif not self.status_check(self.previous.status):
            raise IndicoInputError(
                f"Submission {self.submission_id} does not meet status requirements"
            )

        yield GenerateSubmissionResult(self.submission_id)
        if self.wait:
            yield JobStatus(id=self.previous.id, wait=True, timeout=self.timeout)


class SubmitReview(GraphQLRequest["Job"]):
    """
    Submit an "Auto" Review for a submission. Requires that the submission be in PENDING_AUTO_REVIEW status.

    Args:
        submission_id (int): Id of submission to submit reviewEnabled for

    Options:
        changes (dict, list, or JSONString): changes to make to raw predictions

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
        submission: "Union[int, Submission]",
        changes: "Optional[Union[str, AnyDict, List[AnyDict]]]" = None,
        rejected: bool = False,
        force_complete: "Optional[bool]" = None,
    ):
        changes_json: "Optional[str]" = None
        submission_id = submission if isinstance(submission, int) else submission.id
        if not changes and not rejected:
            raise IndicoInputError("Must provide changes or reject=True")
        elif changes:
            if isinstance(changes, (dict, list)):
                changes_json = json.dumps(changes)
            else:
                changes_json = changes

        _vars = {
            "submissionId": submission_id,
            "changes": changes_json,
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

    def process_response(self, response: "Payload") -> "Job":
        response = super().parse_payload(response)["submitAutoReview"]
        return Job(id=response["jobId"])


class GetReviews(GraphQLRequest["List[SubmissionReviewFull]"]):
    """
    Given a submission Id, return all the full Review objects back with changes

    Args:
        submission_id (int): Id of submission to submit reviewEnabled for
    Options:

    Returns:
        A list of Review objects with changes
    """

    query = """
    query GetReview($submissionId: Int!)
    {
        submission(id: $submissionId) {
            id
            reviews(includeChanges: true) {
                id
                submissionId
                createdAt
                createdBy
                startedAt
                completedAt
                rejected
                reviewType
                notes
                changes
            }
        }
    }
    """

    def __init__(self, submission_id: int):
        super().__init__(self.query, variables={"submissionId": submission_id})

    def process_response(self, response: "Payload") -> "List[SubmissionReviewFull]":
        return [
            SubmissionReviewFull(**review)
            for review in super().parse_payload(response)["submission"]["reviews"]
        ]


class RetrySubmission(GraphQLRequest["List[Submission]"]):
    """
    Given a list of submission ids, retry those failed submissions.
    Submissions must be in a failed state and cannot be requested before
    the cool-off period (typically 180ms).

    Args:
        submission_ids (List[int]): the given submission ids to retry.
    Options:

    Raises:
        IndicoInputError

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

    def __init__(self, submission_ids: "List[int]"):
        if submission_ids is None or len(submission_ids) < 1:
            raise IndicoInputError("You must specify submission ids")

        super().__init__(self.query, variables={"submissionIds": submission_ids})

    def process_response(self, response: "Payload") -> "List[Submission]":
        return [
            Submission(**s) for s in super().parse_payload(response)["retrySubmissions"]
        ]
