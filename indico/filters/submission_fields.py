from typing import TYPE_CHECKING

from indico.filters.base import FilterV2

if TYPE_CHECKING:
    from typing import Any, Dict, Optional, Union


class SubmissionFieldFilter(FilterV2):
    """
    Filter for querying Submission Fields.

    Args:
        status (str, optional): Submission status
        created_at (str | dict, optional): Creation date or date range
        updated_at (str | dict, optional): Update date or date range
        files_deleted (bool, optional): Whether files are deleted
        retrieved (bool, optional): Whether submission is retrieved
        review_in_progress (bool, optional): Whether review is in progress
        field_id (int, optional): Filter by field ID (explicit check)
        custom_fields (dict, optional): Filter by values of specific field IDs.
            Dict of {field_id: value}.
    """

    def __init__(
        self,
        # Standard columns
        status: "Optional[str]" = None,
        created_at: "Optional[Union[str, Dict[str, Any]]]" = None,
        updated_at: "Optional[Union[str, Dict[str, Any]]]" = None,
        files_deleted: "Optional[bool]" = None,
        retrieved: "Optional[bool]" = None,
        review_in_progress: "Optional[bool]" = None,
        # Custom fields
        field_id: "Optional[int]" = None,
        custom_fields: "Optional[Dict[int, Any]]" = None,
    ):
        data = []

        # Standard column mapping
        params = {
            "status": status,
            "createdAt": created_at,
            "updatedAt": updated_at,
            "filesDeleted": files_deleted,
            "retrieved": retrieved,
            "reviewInProgress": review_in_progress,
        }

        for col, val in params.items():
            if val is not None:
                if isinstance(val, list):
                    for item in val:
                        data.append({"column": col, "filter": {"value": item}})
                else:
                    data.append({"column": col, "filter": {"value": val}})

        if field_id is not None:
            data.append({"column": "fieldId", "filter": {"fieldId": field_id}})

        if custom_fields:
            for fid, val in custom_fields.items():
                data.append(
                    {"column": "fieldId", "filter": {"fieldId": fid, "value": val}}
                )

        super().__init__(data=data)
