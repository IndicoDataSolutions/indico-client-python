from typing import TYPE_CHECKING, List, Optional

from indico.client.request import GraphQLRequest
from indico.types import BaseType, JSONType
from indico.typing import AnyDict

if TYPE_CHECKING:
    pass


class SubmissionManagementSubmission(BaseType):
    id: int
    status: str
    files_deleted: bool
    retrieved: bool
    completed_at: Optional[str]
    fields: List[JSONType]
    input_files: List[JSONType]


class SubmissionManagementFieldsPage(BaseType):
    """
    Paginated list of submission management fields.
    """

    submissions: List[SubmissionManagementSubmission]
    cursor: str
    total: int
    field_info: List[JSONType]


class GetSubmissionManagementFields(GraphQLRequest[SubmissionManagementFieldsPage]):
    """
    Query for managing submissions with pagination and filtering.

    Args:
        workflow_id (int): Workflow ID
        field_ids (List[int], optional): List of field IDs
        filters (List[dict], optional): List of filters
        limit (int, optional): Page size
        cursor (str, optional): Pagination cursor
    """

    query = """
    query getSubmissionManagementFields(
        $workflowId: Int!,
        $fieldIds: [Int],
        $filters: [SubmissionColumnFilterInput],
        $cursor: String,
        $limit: Int
    ) {
        submissionManagementFields(
            workflowId: $workflowId,
            fieldIds: $fieldIds,
            filters: $filters,
            cursor: $cursor,
            size: $limit
        ) {
            submissions {
                id
                status
                filesDeleted
                retrieved
                completedAt
                fields {
                    id
                    formattedValue
                }
                inputFiles {
                    id
                    filename
                    status
                }
            }
            fieldInfo {
                id
                name
            }
            cursor
            total
        }
    }
    """

    def __init__(
        self,
        workflow_id: int,
        field_ids: "Optional[List[int]]" = None,
        filters: "Optional[List[AnyDict]]" = None,
        limit: int = 100,
        cursor: "Optional[str]" = None,
    ):
        super().__init__(
            self.query,
            variables={
                "workflowId": workflow_id,
                "fieldIds": field_ids,
                "filters": filters,
                "limit": limit,
                "cursor": cursor,
            },
        )

    def process_response(self, response: "AnyDict") -> SubmissionManagementFieldsPage:
        return SubmissionManagementFieldsPage(
            **super().parse_payload(response)["submissionManagementFields"]
        )
