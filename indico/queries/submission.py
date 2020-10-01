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
    List all Submissions visible to the authenticated user

    Args:
        submission_ids (List[int], optional): Submission ids to filter by
        workflow_ids (List[int], optional): Workflow ids to filter by
        filters (SubmissionFilter or Dict, optional): Submission attributes to filter by
        limit (int, optional): Maximum number of Submissions to return. Defaults to 1000

    Returns:
        List[Submission]: All the found Submission objects
    """

    query = """
        query ListSubmissions(
            $submissionIds: [Int],
            $workflowIds: [Int],
            $filters: SubmissionFilter,
            $limit: Int
        ){
            submissions(
                submissionIds: $submissionIds,
                workflowIds: $workflowIds,
                filters: $filters,
                limit: $limit
            ){
                submissions {
                    id
                    datasetId
                    workflowId
                    status
                    inputFile
                    inputFilename
                    resultFile
                    errors
                }
            }
        }
    """

    def __init__(
        self,
        submission_ids: List[int] = None,
        workflow_ids: List[int] = None,
        filters: Union[Dict, SubmissionFilter] = None,
        limit: int = 1000,
    ):
        super().__init__(
            self.query,
            variables={
                "submissionIds": submission_ids,
                "workflowIds": workflow_ids,
                "filters": filters,
                "limit": limit,
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
                errors
            }
        }
    """

    def __init__(
        self, submission_id: int,
    ):
        super().__init__(
            self.query, variables={"submissionId": submission_id},
        )

    def process_response(self, response) -> Submission:
        return Submission(**(super().process_response(response)["submission"]))


class UpdateSubmission(GraphQLRequest):
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
        super().__init__(
            self.query, variables={"submissionId": submission_id},
        )

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
