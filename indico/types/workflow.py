from enum import Enum
from typing import List, Union

from indico.types import BaseType, ModelGroup, ModelTaskType


class WorkflowComponent(BaseType):
    """
    A component, such as a Model Group or Content Length filter, that is present on a workflow.
    This is essentially a step in the workflow process, such as OCR
    or predicting with a model group.

    """
    id: int
    component_type: str
    task_type: str
    model_type: str
    model_group: ModelGroup
    task_type: str
    model_type: str
    minimum: int
    maximum: int


class WorkflowComponentLinks(BaseType):
    """
    Represents a link between two components.
    """
    id: int
    head_component_id: int
    tail_component_id: int


class Workflow(BaseType):
    """
    Represents a Workflow in the Indico Data Platform.
    """
    id: int
    name: str
    status: str
    review_enabled: bool
    auto_review_enabled: bool
    components: List[WorkflowComponent]
    component_links: List[WorkflowComponentLinks]

    def component_by_type(self, component_type: str) -> WorkflowComponent:
        """
        Returns first component available of type specified.
        """
        return next(component for component in self.components if component.component_type == component_type)

    def model_group_by_name(self, name: str) -> WorkflowComponent:
        """
        Returns first model group component of name specified.
        """
        return next(component for component in self.components if hasattr(component, "model_group")
                    and component.model_group.name == name)


class LinkedLabelStrategy(Enum):
    BY_ROW = 0,
    BY_KEY = 1


class LinkedLabelGroup:
    def __init__(self, name: str, strategy: LinkedLabelStrategy, class_ids: List[int], strategy_settings: dict):
        self.name = name
        self.strategy = strategy
        self.class_ids = class_ids
        self.strategy_settings = strategy_settings
