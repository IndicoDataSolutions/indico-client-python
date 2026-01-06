from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any, List, Optional


class FieldBlueprintFilter(dict):
    """
    Filter for querying Field Blueprints.

    Usage:
        Logical: FieldBlueprintFilter(op="and", filters=[...])
        Condition: FieldBlueprintFilter(op="eq", field="field_blueprint.uid", value="123")
    """

    def __init__(
        self,
        op: "Optional[str]" = None,
        filters: "Optional[List[dict]]" = None,
        field: "Optional[str]" = None,
        value: "Optional[Any]" = None,
    ):
        data = {
            "op": op,
            "filters": filters,
            "field": field,
            "value": value,
        }
        # Remove None values to keep payload clean
        clean_data = {k: v for k, v in data.items() if v is not None}
        super().__init__(**clean_data)
