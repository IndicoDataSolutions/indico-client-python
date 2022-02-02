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
    Query to generate a Document Report.
    Generates a paged request and paged response.
    See examples for a sample query.
    """

    query = """
       query SubmissionsLog($filters: SubmissionLogFilter, $limit: Int, $after: Int){
          submissionsLog(filters: $filters, limit: $limit, after: $after){
            submissions{
              datasetId
              workflowId
              status
              createdAt
              updatedAt
              updatedBy
              completedAt
              errors
              retrieved
              inputFiles{
                filename
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
        self, filters: Union[dict, DocumentReportFilter] = None, limit: int = None
    ):
        variables = {"filters": filters, "limit": limit}
        super().__init__(self.query, variables=variables)

    def process_response(self, response):
        return _DocumentReportList(
            **super().process_response(response)["submissionsLog"]
        ).submissions
