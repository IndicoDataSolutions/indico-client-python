from typing import TYPE_CHECKING, Any, List, Optional

if TYPE_CHECKING:
    from typing import Any, Optional


class FieldBlueprintFilter(dict[str, Any]):
    """
    Filter for querying Field Blueprints.

    :param op: The operator to apply.
        - Logical: "and", "or", "not" (requires `filters`)
        - Comparison: "eq", "neq", "gt", "lt", "ge", "le", "in", "contains" (requires `field` and `value`)
    :param filters: A list of `FieldBlueprintFilter` instances. Required if `op` is logical (e.g., "and").
    :param field: The database field path to filter on. Required if `op` is a comparison.
        Format: "table.column" or "table.column.nested.key" (for JSONB).
        Examples: "field_blueprint.uid", "field_blueprint.prompt_config.prompt"

        Queryable Fields:
        - "field_blueprint.id" (Int)
        - "field_blueprint.uid" (String)
        - "field_blueprint.name" (String)
        - "field_blueprint.version" (String)
        - "field_blueprint.task_type" (Enum: GENAI_ANNOTATION, SUMMARIZATION)
        - "field_blueprint.tags" (List[String])
        - "field_blueprint.enabled" (Boolean)
        - "field_blueprint.field_config" (JSONB)
        - "field_blueprint.prompt_config" (JSONB)

        Note: JSONB fields (field_config, prompt_config) support nested path querying.
        e.g., "field_blueprint.prompt_config.target_name"
    :param value: The value to filter by. Required if `op` is a comparison.
        - For "eq", "neq", "gt", "lt", "ge", "le": A scalar value (str, int, float, etc.)
        - For "in": A list of values
        - For "contains": A string substring

    Usage:
        Logical: FieldBlueprintFilter(op="and", filters=[...])
        Condition: FieldBlueprintFilter(op="eq", field="field_blueprint.uid", value="123")
    """

    def __init__(
        self,
        op: Optional[str] = None,
        filters: Optional[List["FieldBlueprintFilter"]] = None,
        field: Optional[str] = None,
        value: Optional[Any] = None,
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
