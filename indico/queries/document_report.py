""""""

from typing import TYPE_CHECKING, List

from indico import PagedRequest
from indico.filters import DocumentReportFilter
from indico.types import BaseType
from indico.types.document_report import DocumentReport

if TYPE_CHECKING:  # pragma: no cover
    from typing import Optional, Union

    from indico.typing import AnyDict, Payload


class _DocumentReportList(BaseType):
    submissions: List[DocumentReport]


class GetDocumentReport(PagedRequest["List[DocumentReport]"]):
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
        filters: "Optional[Union[AnyDict, DocumentReportFilter]]" = None,
        limit: "Optional[int]" = None,
        all_submissions: bool = False,
    ):
        variables = {
            "filters": filters,
            "limit": limit,
            "allSubmissions": all_submissions,
        }
        super().__init__(self.query, variables=variables)

    def process_response(self, response: "Payload") -> "List[DocumentReport]":
        return _DocumentReportList(
            **super().parse_payload(response)["submissionsLog"]
        ).submissions
