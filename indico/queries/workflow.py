from typing import List

from indico.client.request import (
    GraphQLRequest,
    HTTPMethod,
    HTTPRequest,
    RequestChain,
)
from indico.errors import IndicoError
from indico.queries.storage import UploadDocument
from indico.types.jobs import Job
from indico.types.workflow import Workflow


class ListWorkflowsForDataset(GraphQLRequest):
    """
    List all of the workflows for a dataset

    Args:
        dataset_id (int): id of the dataset to list workflows.

    Returns:
        Workflows: List of Workflow objects for the given dataset_id
    """

    query = """
        query ListWorkflows($datasetId: Int){
	        workflows(datasetIds: [$datasetId]){
                workflows {
                    id
                    name
                }
            }
        }
    """

    def __init__(self, dataset_id: int):
        super().__init__(self.query, variables={"datasetId": dataset_id})

    def process_response(self, response):
        return [
            Workflow(**w)
            for w in super().process_response(response)["workflows"]["workflows"]
        ]


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
    Submit a list of PDF or CSV files to a workflow

    Args:
        files (str): List of file paths containing content to submit to the workflow
        workflow_id (int): id of the workflow to run.

    Returns:
        Job: Job object for the workflow submission
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
