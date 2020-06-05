import json
from typing import Dict, List

from indico.client.request import GraphQLRequest
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
        filters: Dict[str, Any] = None,
        limit: int = None,
    ):
        super().__init__(
            self.query,
            variables={
                "submissionIds": submission_ids,
                "workflowIds": workflow_ids,
                "filters": json.dumps(filters) if filters else None,
                "limit": limit,
            },
        )

    def process_response(self, response) -> List[Submission]:
        return [
            Submission(**s)
            for s in super().process_response(response)["submissions"]["submissions"]
        ]


class SubmissionResult(GraphQLRequest):
    query = """
        mutation CreateSubmissionResults($submissionId: Int!) {
            submissionResults(submissionId: $submissionId) {
                jobId
            }
        }

    """

    def __init__(
        self, submission_id: int,
    ):
        super().__init__(
            self.query, variables={"submissionId": submission_id},
        )

    def process_response(self, response) -> Job:
        response = super().process_response(response)["submissionResults"]
        return Job(id=response["jobId"])
