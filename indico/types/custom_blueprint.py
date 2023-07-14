import typing as t
from indico.types import BaseType


class TaskBlueprint(BaseType):
    id: int
    name: str
    component_family: str
    icon: str
    description: str
    footer: str
    tags: t.List[str]
    enabled: bool
    config: t.Dict
