from functools import partial
from operator import eq, ne
from typing import Dict, List, Union

from indico.client.request import Debouncer, GraphQLRequest, RequestChain
from indico.errors import IndicoInputError
from indico.filters import SubmissionFilter
from indico.queries import JobStatus
from indico.types import Job, Submission


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


class GenerateSubmissionResult(GraphQLRequest):
    query = """
        mutation CreateSubmissionResults($submissionId: Int!) {
            submissionResults(submissionId: $submissionId) {
                jobId
            }
        }

    """

    def __init__(
        self, submission_id: int
    ):
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
        submission_id (int): Id of the submission
        check_status (str, optional): Submission status to check for.
            Defaults to any status other than `PROCESSING`
        wait (bool, optional): Wait until the submission is `check_status`
            and wait for the result file to be generated. Defaults to False
        timeout (int or float, optional): Maximum number of seconds to wait before
            timing out. Ignored if not `wait`. Defaults to 30

    Returns:
        If `wait`:
            str: URL to result file that can be retrieved with `RetrieveStorageObject`

        If not `wait`:
            Job: Job that can be watched for results

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
        submission_id: int,
        check_status: str = None,
        wait: bool = False,
        timeout: Union[int, float] = 30,
    ):
        self.submission_id = submission_id
        self.wait = wait
        self.timeout = timeout
        self.status_check = (
            partial(eq, check_status) if check_status else partial(ne, "PROCESSING")
        )

    def requests(self) -> Union[Job, str]:
        yield GetSubmission(self.submission_id)
        debouncer = Debouncer(max_timeout=self.timeout)
        if self.wait:
            while not self.status_check(self.previous):
                yield GetSubmission(self.submission_id)
                debouncer.backoff()
        elif not self.status_check(self.previous):
            raise IndicoInputError(
                f"Submission {self.submission_id} does not meet status requirements"
            )

        yield GenerateSubmissionResult(
            self.submission_id
        )
        if self.wait:
            yield JobStatus(id=self.previous.id, wait=True, timeout=self.timeout)
