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


class ModelGroupComponentArguments:
    dataset_id: int
    workflow_id: int
    subset_id: int
    labelset_column_id: int
    source_column_id: int
    model_type: ModelTaskType
