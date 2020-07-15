from typing import List

from indico.client.request import GraphQLRequest, RequestChain
from indico.errors import IndicoError
from indico.queries.storage import UploadDocument
from indico.types import Job, Workflow


class ListWorkflows(GraphQLRequest):
    """
    List all workflows visible to authenticated user

    Args:
        dataset_ids (List[int], optional): List of dataset ids to filter by.
            Defaults to None
        workflow_ids (List[int], optional): List of workflow ids to filter by
            Defaults to None

    Returns:
        List[Workflow]: All the found Workflow objects
    """

    query = """
        query ListWorkflows($datasetIds: [Int], $workflowIds: [Int]){
            workflows(datasetIds: $datasetIds, workflowIds: $workflowIds){
                workflows {
                    id
                    name
                    reviewEnabled
                }
            }
        }
    """

    def __init__(self, dataset_ids: List[int] = None, workflow_ids: List[int] = None):
        super().__init__(
            self.query,
            variables={"datasetIds": dataset_ids, "workflowIds": workflow_ids},
        )

    def process_response(self, response) -> List[Workflow]:
        return [
            Workflow(**w)
            for w in super().process_response(response)["workflows"]["workflows"]
        ]


class GetWorkflow(ListWorkflows):
    """
    Query for Workflow by id

    Args:
        workflow_id (int): Workflow id to query for

    Returns:
        Workflow: Found Workflow object
    """

    def __init__(self, workflow_id: int):
        super().__init__(workflow_ids=[workflow_id])

    def process_response(self, response) -> Workflow:
        return super().process_response(response)[0]


class _WorkflowSubmission(GraphQLRequest):

    query = """
        mutation workflowSubmissionMutation($workflowId: Int!, $files: [FileInput]!) {
            workflowSubmission(workflowId: $workflowId, files: $files) {
                jobIds
                submissionIds
            }
        }
    """

    def __init__(self, workflow_id: int, files: List[str], submission: bool):
        self.workflow_id = workflow_id
        self.record_submission = submission
        super().__init__(
            query=self.query,
            variables={
                "files": files,
                "workflowId": workflow_id,
                "recordSubmission": submission,
            },
        )

    def process_response(self, response):
        response = super().process_response(response)["workflowSubmission"]
        if self.record_submission:
            return response["submissionIds"]
        elif not not response["jobIds"]:
            raise IndicoError(f"Failed to submit to workflow {self.workflow_id}")
        return [Job(id=job_id) for job_id in response["jobIds"]]


class WorkflowSubmission(RequestChain):
    """
    Submit files to a workflow for processing

    Args:
        files (List[str]): List of local file paths to submit
        workflow_id (int): Id of workflow to submit files to
        submission (bool, optional): Process these files as normal submissions.
            Defaults to True.
            If False, files will be processed as AsyncJobs, ignoring any workflow
            post-processing steps like Review and with no record in the system

    Returns:
        List[int]: If `submission`, these will be submission ids.
            Otherwise, they will be AsyncJob ids.

    """

    def __init__(self, files: List[str], workflow_id: int, submission: bool = True):
        self.files = files
        self.workflow_id = workflow_id
        self.submission = submission

    def requests(self):
        yield UploadDocument(files=self.files)
        yield _WorkflowSubmission(
            files=self.previous,
            workflow_id=self.workflow_id,
            submission=self.submission,
        )
