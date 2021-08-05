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
    query = """
           query SubmissionsLog($filters: SubmissionLogFilter, $limit: Int){
  submissionsLog(filters: $filters, limit: $limit){
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

    def __init__(self, filters: Union[dict, DocumentReportFilter] = None, limit: int = None):
        variables = {
            "filters": filters,
            "limit": limit
        }
        super().__init__(self.query, variables=variables)

    def process_response(self, response):
        return _DocumentReportList(**super().process_response(response)["submissionsLog"]).submissions
