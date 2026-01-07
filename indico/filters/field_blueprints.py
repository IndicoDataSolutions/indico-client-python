from typing import TYPE_CHECKING, Any, List, Optional

if TYPE_CHECKING:
    from typing import Any, Optional


class FieldBlueprintFilter(dict[str, Any]):
    """
    Filter for querying Field Blueprints.

    Args:
        op (str, optional): The operator to apply. Use `FieldBlueprintFilter.LogicalOp` or `FieldBlueprintFilter.ComparisonOp` constants.
        filters (list, optional): A list of `FieldBlueprintFilter` instances. Required if `op` is LogicalOp.
        field (str, optional): The database field path to filter on. Use `FieldBlueprintFilter.Field` constants.
        value (Any, optional): The value to filter by. Required if `op` is ComparisonOp.
    """

    class Field:
        ID = "field_blueprint.id"
        UID = "field_blueprint.uid"
        NAME = "field_blueprint.name"
        VERSION = "field_blueprint.version"
        TASK_TYPE = "field_blueprint.task_type"
        TAGS = "field_blueprint.tags"
        ENABLED = "field_blueprint.enabled"
        FIELD_CONFIG = "field_blueprint.field_config"
        PROMPT_CONFIG = "field_blueprint.prompt_config"

    class LogicalOp:
        AND = "and"
        OR = "or"
        NOT = "not"

    class ComparisonOp:
        EQ = "eq"
        NEQ = "neq"
        GT = "gt"
        LT = "lt"
        GE = "ge"
        LE = "le"
        IN = "in"
        CONTAINS = "contains"

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
