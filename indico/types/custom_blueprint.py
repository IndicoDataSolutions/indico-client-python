import typing as t
from indico.types import BaseType
from indico.types.workflow import ComponentFamily


class TaskLauncher(BaseType):
    service: str
    name: str


class IODef(BaseType):
    name: str
    io_class: str


class BlueprintConfig(BaseType):
    submission_launcher: TaskLauncher
    inputs: t.List[IODef]
    outputs: t.List[IODef]
    custom_config: t.Dict = None
    overrides: t.List[str] = None


class FieldDataInput(BaseType):
    name: str


class ModelConfig(BlueprintConfig):
    data_type: str
    task_type: str
    fields: t.List[FieldDataInput]


class FilterConfig(BlueprintConfig):
    branches: t.List[str]
    links: t.List[t.List[str]]
    data_type: str = None


class OutputConfig(BlueprintConfig):
    data_type: str = None


class TaskBlueprint(BaseType):
    id: int
    name: str
    component_family: ComponentFamily
    icon: str
    description: str
    footer: str
    tags: t.List[str]
    enabled: bool
    config: t.Dict
