# -*- coding: utf-8 -*-
from typing import TYPE_CHECKING

from indico.types.base import BaseType

if TYPE_CHECKING:  # pragma: no cover
    from typing import Any, List, Optional

    from indico.typing import AnyDict


class FieldBlueprint(BaseType):
    """
    A Field Blueprint in the Indico Platform.

    Attributes:
        id (int): ID of the field blueprint
        uid (str): Unique identifier for the field blueprint
        name (str): Display name of the field blueprint
        version (str): Version of the field blueprint
        task_type (str): Task type this blueprint is designed for
        description (str): Description of the field blueprint
        enabled (bool): Whether the field blueprint is enabled
        created_at (str): Creation timestamp
        updated_at (str): Last update timestamp
        created_by (int): ID of the user who created the blueprint
        updated_by (int): ID of the user who last updated the blueprint
        tags (List[str]): List of tags
        field_config (dict): Configuration for the field
        prompt_config (dict): Configuration for the prompt
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
    tags: "List[str]"
    field_config: "AnyDict"
    prompt_config: "AnyDict"
    description: "Optional[str]"

    def __init__(self, **kwargs: "Any"):
        super().__init__(**kwargs)
