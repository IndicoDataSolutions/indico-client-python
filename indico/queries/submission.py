import json
from typing import Dict, List, Union

from indico.client.request import GraphQLRequest
from indico.filters import SubmissionFilter
from indico.queries import JobStatus
from indico.types import Job, Submission


class ListSubmissions(GraphQLRequest):
    query = """
        query ListSubmissions($submissionIds: [Int], $workflowIds: [Int], $filters: SubmissionFilter, $limit: Int){
	        submissions(submissionIds: $submissionIds, workflowIds: $workflowIds, filters: $filters, limit: $limit){
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
        if isinstance(filters, dict):
            filters = SubmissionFilter.from_dict(filters)

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


class CreateSubmissionResult(GraphQLRequest):
    query = """
        mutation CreateSubmissionResults($submissionId: Int!) {
            submissionResults(submissionId: $submissionId) {
                jobId
            }
        }

    """

    def __init__(self, submission_id: int, wait: bool = False):
        self.wait = wait
        super().__init__(
            self.query, variables={"submissionId": submission_id},
        )

    def process_response(self, response) -> Job:
        response = super().process_response(response)["submissionResults"]
        job = Job(id=response["jobId"])
        if self.wait:
            return JobStatus(id=job.id, wait=True).result
        return job
