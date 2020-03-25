import json
from typing import List
from indico.client.request import RequestChain, GraphQLRequest, HTTPMethod, HTTPRequest
from indico.types.jobs import Job
from indico.types.workflow import Workflow
from indico.queries.storage import UploadDocument
from indico.errors import IndicoError


class ListWorkflowsForDataset(GraphQLRequest):

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
                jobId
            }
        }
    """

    def __init__(self, workflow_id, files: List[str]):
        self.workflow_id = workflow_id
        super().__init__(
            query=self.query, variables={"files": files, "workflowId": workflow_id}
        )

    def process_response(self, response):
        job_id = super().process_response(response)["workflowSubmission"]["jobId"]
        if not job_id:
            raise IndicoError(f"Failed to submit to workflow {self.workflow_id}")
        return Job(id=job_id)


class WorkflowSubmission(RequestChain):
    def __init__(self, files: List[str], workflow_id: int):
        self.files = files
        self.workflow_id = workflow_id

    def requests(self):
        yield UploadDocument(files=self.files)
        yield _WorkflowSubmission(files=self.previous, workflow_id=self.workflow_id)
