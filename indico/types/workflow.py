from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, List, Optional

from indico.types import BaseType, ModelGroup
from indico.types.base import JSONType

if TYPE_CHECKING:  # pragma: no cover
    from indico.typing import AnyDict


class ComponentToDeleteInfo(BaseType):
    id: int
    name: str
    component_type: str
    model_group_name: Optional[str]
    reason: str


class LinkInfoBase(BaseType):
    head_id: int
    tail_id: int
    config: JSONType


class LinkToAddInfo(LinkInfoBase):
    pass


class LinkToRemoveInfo(LinkInfoBase):
    id: int


class LinkToUpdateInfo(LinkInfoBase):
    id: int


class ComponentValidationResult(BaseType):
    valid: bool
    components_to_delete: List[ComponentToDeleteInfo]
    links_to_remove: List[LinkToRemoveInfo]
    links_to_update: List[LinkToUpdateInfo]
    links_to_add: List[LinkToAddInfo]


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
    minimum: int
    maximum: int


class WorkflowComponentLinks(BaseType):
    """
    Represents a link between two components.
    """

    id: int
    head_component_id: int
    tail_component_id: int
    config: JSONType


class Workflow(BaseType):
    """
    Represents a Workflow in the Indico Data Platform.
    """

    id: int
    name: str
    status: str
    dataset_id: int
    review_enabled: bool
    auto_review_enabled: bool
    components: List[WorkflowComponent]
    component_links: List[WorkflowComponentLinks]
    created_by: int
    created_at: datetime
    submission_runnable: bool

    def component_by_type(self, component_type: str) -> WorkflowComponent:
        """
        Returns first component available of type specified.
        """
        return next(
            component
            for component in self.components
            if component.component_type == component_type
        )

    def model_group_by_name(self, name: str) -> WorkflowComponent:
        """
        Returns first model group component of name specified.
        """
        return next(
            component
            for component in self.components
            if hasattr(component, "model_group") and component.model_group.name == name
        )


class LinkedLabelStrategy(Enum):
    BY_ROW = 0
    BY_KEY = 1


class LinkedLabelGroup:
    def __init__(
        self,
        name: str,
        strategy: LinkedLabelStrategy,
        class_ids: List[int],
        strategy_settings: "AnyDict",
    ):
        self.name = name
        self.strategy = strategy
        self.class_ids = class_ids
        self.strategy_settings = strategy_settings


class ComponentFamily(Enum):
    MODEL = 0
    FILTER = 1
    TRANSFORMER = 2
    REVIEW = 3
    OUTPUT = 4
