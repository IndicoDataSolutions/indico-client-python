from typing import Any, List, Optional

from indico.types.base import BaseType
from indico.typing import AnyDict


class FieldBlueprint(BaseType):
    """
    A Field Blueprint in the Indico Platform.
    ...
    """

    id: int
    uid: str
    name: str
    version: str
    task_type: str
    enabled: bool
    created_at: str
    updated_at: str
    created_by: int
    updated_by: int
    tags: List[str]
    field_config: AnyDict
    prompt_config: AnyDict
    description: Optional[str]

    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)
