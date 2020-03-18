import json
from typing import List
from indico.client.request import RequestChain, GraphQLRequest, HTTPMethod, HTTPRequest
from indico.types.jobs import Job
from indico.queries.storage import UploadDocument

class _WorkflowSubmission(GraphQLRequest):
    query =""""
        mutation workflowSubmissionMutation($workflowId: Int!, $files: [FileInput]!) {
            workflowSubmission(workflowId: $workflowId, files: $files) {
                    jobId
            }
    }"""

    def __init__(self, workflow_id, files: List[str]):
        super().__init__(query=self.query, variables={
            "files": files,
            "workflowId": workflow_id
        })

    def process_response(self, response):
        jobs = super().process_response(response)["workflowSubmission"]["jobIds"]
        if jobs:
            return [Job(id=j) for j in jobs]
        else: 
            return []


class WorkflowSubmission(RequestChain):
    def __init__(self, files: List[str], workflow_id: int):
        self.files = files
        self.workflow_id = workflow_id    
    def requests(self):
        yield UploadDocument(files=self.files)
        yield _WorkflowSubmission(files=self.previous, workflow_id=self.workflow_id)