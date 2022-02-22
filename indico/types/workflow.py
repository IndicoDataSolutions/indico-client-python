from typing import List, Union

from indico.types import BaseType, ModelGroup, ModelTaskType


class WorkflowValidActions(BaseType):
    """
    ValidActions represents components that can be added after an existing component.
    this is becoming:
    validActions {
          operation
          componentFamily
          componentType
          subType
        }
    """
    addModel: [str]
    addFilter: [str]
    addTransformer: [str]


class WorkflowComponent(BaseType):
    """

    """
    id: int
    component_type: str
    #valid_actions: WorkflowValidActions
    task_type: str
    model_type: str
    model_group: ModelGroup
    task_type: str
    model_type: str

class WorkflowComponentLinks(BaseType):
    id: int
    head_component_id: int
    tail_component_id: int

    #valid_actions: WorkflowValidActions


class Workflow(BaseType):
    id: int
    name: str
    status: str
    review_enabled: bool
    auto_review_enabled: bool
    components: List[WorkflowComponent]
    component_links: List[WorkflowComponentLinks]

    def component_by_type(self, component_type: str) -> WorkflowComponent:
        return next(component for component in self.components if component.component_type == component_type)

    def model_group_by_name(self, name: str) -> WorkflowComponent:
        return next(component for component in self.components if hasattr(component, "model_group")
                    and component.model_group.name == name)

class ModelGroupComponentArguments:
    dataset_id: int
    workflow_id: int
    subset_id: int
    labelset_column_id: int
    source_column_id: int
    model_type: ModelTaskType
