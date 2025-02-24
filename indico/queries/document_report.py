""""""

from typing import List, Union

from indico import PagedRequest
from indico.filters import DocumentReportFilter
from indico.types import BaseType
from indico.types.document_report import DocumentReport


class _DocumentReportList(BaseType):
    submissions: List[DocumentReport]
    pass


class GetDocumentReport(PagedRequest):
    """
    Query to generate a Document Report, otherwise known as a log of past submissions.
    """

    query = """
       query SubmissionsLog($filters: SubmissionLogFilter, $limit: Int, $after: Int, $allSubmissions: Boolean){
          submissionsLog(filters: $filters, limit: $limit, after: $after, allSubmissions: $allSubmissions){
            submissions{
              datasetId
              workflowId
              status
              createdAt
              createdBy
              updatedAt
              updatedBy
              completedAt
              errors
              retrieved
              submissionId
              filesDeleted
              inputFiles{
                id
                filename
                filepath
                submissionId
                fileSize
                numPages
              }
            }
            pageInfo{
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
        filters: Union[dict, DocumentReportFilter] = None,
        limit: int = None,
        all_submissions=False,
    ):
        variables = {
            "filters": filters,
            "limit": limit,
            "allSubmissions": all_submissions,
        }
        super().__init__(self.query, variables=variables)

    def process_response(self, response):
        return _DocumentReportList(
            **super().process_response(response)["submissionsLog"]
        ).submissions
