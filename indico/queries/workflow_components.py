from typing import TYPE_CHECKING, cast

import jsons

from indico import GraphQLRequest, RequestChain
from indico.errors import IndicoInputError
from indico.queries.model_import import UploadStaticModelExport
from indico.types import (
    LinkedLabelGroup,
    NewLabelsetArguments,
    NewQuestionnaireArguments,
    Workflow,
)
from indico.types.workflow import ComponentValidationResult

if TYPE_CHECKING:  # pragma: no cover
    from typing import Any, Iterator, List, Optional, Union

    from indico.typing import AnyDict, Payload


class _AddWorkflowComponent(GraphQLRequest["Workflow"]):
    query = """
        mutation addWorkflowComponent($afterComponentId: Int, $afterComponentLinkId: Int, $component: JSONString!, $workflowId: Int!, $blueprintId: Int) {
        addWorkflowComponent(
            afterComponentId: $afterComponentId
            component: $component
            workflowId: $workflowId
            afterComponentLinkId: $afterComponentLinkId
            blueprintId: $blueprintId
        ) {
            workflow {
            id
            components {
                id
                componentType
                reviewable
                ... on ContentLengthComponent {
                minimum
                maximum
                }
                filteredClasses
                ... on ModelGroupComponent {
                taskType
                modelType
                modelGroup {
                    status
                    id
                    classNames
                    name
                    taskType
                    questionnaireId
                    selectedModel {
                    id
                    }
                }
                }
            }
            componentLinks {
                id
                headComponentId
                tailComponentId
                filters {
                classes
                }
            }
            }
        }
        }
    """

    def __init__(
        self,
        after_component_id: "Optional[int]",
        after_component_link: "Optional[int]",
        workflow_id: int,
        component: "AnyDict",
        blueprint_id: "Optional[int]" = None,
    ):
        super().__init__(
            self.query,
            variables={
                "afterComponentId": after_component_id,
                "afterComponentLinkId": after_component_link,
                "workflowId": workflow_id,
                "component": jsons.dumps(component),
                "blueprintId": blueprint_id,
            },
        )

    def process_response(self, response: "Payload") -> "Workflow":
        return Workflow(
            **super().parse_payload(response)["addWorkflowComponent"]["workflow"]
        )


class AddLinkedLabelComponent(RequestChain["Workflow"]):
    """
    Adds a linked label transformer that groups together labels

    Args:
        after_component_id(int): the component this component follows.
        after_component_link_id(int): the component link this component follows.
        workflow_id(int): the workflow id.
        labelset_id(int): the labelset to source classes from.
        model_group_id(int): the model group to source classes from.
        groups (List[LinkedLabelGroup]): configuration for how to group labels.
    """

    def __init__(
        self,
        after_component_id: int,
        workflow_id: int,
        labelset_id: int,
        model_group_id: int,
        groups: "List[LinkedLabelGroup]",
        after_component_link_id: "Optional[int]" = None,
    ):
        self.workflow_id = workflow_id
        self.after_component_id = after_component_id
        self.after_component_link_id = after_component_link_id
        self.component = {
            "component_type": "link_label",
            "config": {
                "labelset_id": labelset_id,
                "model_group_id": model_group_id,
                "groups": [self.__groups_to_json(group) for group in groups],
            },
        }

    def __groups_to_json(self, group: "LinkedLabelGroup") -> "AnyDict":
        return {
            "name": group.name,
            "strategy": group.strategy.name.lower(),
            "class_names": group.class_ids,
            "strategy_settings": group.strategy_settings,
        }

    def requests(self) -> "Iterator[_AddWorkflowComponent]":
        yield _AddWorkflowComponent(
            after_component_id=self.after_component_id,
            after_component_link=self.after_component_link_id,
            workflow_id=self.workflow_id,
            component=self.component,
        )


class AddContentLengthFilterComponent(RequestChain["Workflow"]):
    """
    Adds a content length filter.

    Args:
        workflow_id(int): the workflow id.
        after_component_id(int): the component this component follows.
        minimum(int): minimum length of content to accept. Defaults to None.
        maximum(int): maximum length of content to accept. Defaults to None.
    """

    def __init__(
        self,
        workflow_id: int,
        after_component_id: int,
        after_component_link_id: "Optional[int]" = None,
        minimum: "Optional[int]" = None,
        maximum: "Optional[int]" = None,
    ):
        self.workflow_id = workflow_id
        self.after_component_id = after_component_id
        self.after_component_link_id = after_component_link_id
        self.minimum = minimum
        self.maximum = maximum
        self.component = {
            "component_type": "content_length",
            "config": {"minimum": minimum, "maximum": maximum},
        }

    def requests(self) -> "Iterator[_AddWorkflowComponent]":
        yield _AddWorkflowComponent(
            after_component_id=self.after_component_id,
            after_component_link=self.after_component_link_id,
            workflow_id=self.workflow_id,
            component=self.component,
        )


class AddLinkClassificationComponent(RequestChain["Workflow"]):
    """
    Adds a link classification model component with filtered classes.

    Args:
        workflow_id(int): the workflow id.
        after_component_id(int): the component this component follows.
        model_group_id(int): the model group to source classes from.
        filtered_classes(List[List[str]]): sets of classes to filter, i.e., [["A"], ["A","B"]]
        labels(str): decides if to use "actual" or "predicted" labels.
    """

    def __init__(
        self,
        workflow_id: int,
        after_component_id: int,
        model_group_id: int,
        filtered_classes: "List[List[str]]",
        labels: "Optional[str]" = None,
        after_component_link_id: "Optional[int]" = None,
    ):
        self.workflow_id = workflow_id
        self.after_component_id = after_component_id
        self.after_component_link_id = after_component_link_id
        self.component = {
            "component_type": "link_classification_model",
            "config": {
                "model_group_id": model_group_id,
                "filtered_classes": filtered_classes,
                "labels": labels,
            },
        }

    def requests(self) -> "Iterator[_AddWorkflowComponent]":
        yield _AddWorkflowComponent(
            after_component_id=self.after_component_id,
            after_component_link=self.after_component_link_id,
            workflow_id=self.workflow_id,
            component=self.component,
        )


class AddModelGroupComponent(GraphQLRequest["Workflow"]):
    """
    Adds a new model group to a workflow, optionally with a customized questionnaire.
    Available on 5.0+ only.
    Returns workflow with updated component list, which will contain the added Model Group.

    Args:
        workflow_id(int): the id of the workflow to add the component to.
        dataset_id(int): the id of the dataset of this workflow/model group.
        name(str): name of the model group.
        source_column_id(str): source column identifier from dataset.
        after_component_id(str): the id of the previous component, or step, that should precede this step.
            Typically, this prior component would be something like "INPUT_OCR_EXTRACTION" or "INPUT_IMAGE" and can
            be found by using "component_by_type()" on the parent workflow.
        labelset_column_id(int): the labelset column to copy from.
        new_labelset_args(NewLabelsetArguments): if needed, new labelset to add.
            Only use if not using labelset_column_id.
        new_questionnaire_args(NewQuestionnaireArguments): Customize the questionnaire associated with this model group.
        blueprint_id(int): the id of the blueprint to add the model group to.
    """

    query = """
        mutation addModelGroup($workflowId: Int!, $name: String!, $datasetId: Int!, $sourceColumnId: Int!, $afterComponentId: Int, $labelsetColumnId: Int, $afterLinkId: Int, $newLabelsetArgs: NewLabelsetInput, $questionnaireArgs: QuestionnaireInput, $modelTrainingOptions: JSONString, $modelType: ModelType, $blueprintId: Int) {
        addModelGroupComponent(
            workflowId: $workflowId
            name: $name
            datasetId: $datasetId
            sourceColumnId: $sourceColumnId
            afterComponentId: $afterComponentId
            afterLinkId: $afterLinkId
            labelsetColumnId: $labelsetColumnId
            modelTrainingOptions: $modelTrainingOptions
            newLabelsetArgs: $newLabelsetArgs
            questionnaireArgs: $questionnaireArgs
            modelType: $modelType
            blueprintId: $blueprintId
        ) {
            workflow {
            id
            components {
                id
                componentType
                reviewable
                filteredClasses
                ... on ContentLengthComponent {
                minimum
                maximum
                }
                ... on ModelGroupComponent {
                taskType
                modelType
                modelGroup {
                    status
                    id
                    name
                    taskType
                    classNames
                    questionnaireId
                    selectedModel {
                    id
                    }
                }
                }
            }
            componentLinks {
                id
                headComponentId
                tailComponentId
                filters {
                classes
                }
            }
            }
        }
        }
    """

    def __init__(
        self,
        workflow_id: int,
        dataset_id: int,
        name: str,
        source_column_id: int,
        after_component_id: "Optional[int]" = None,
        after_link_id: "Optional[int]" = None,
        labelset_column_id: "Optional[int]" = None,
        new_labelset_args: "Optional[NewLabelsetArguments]" = None,
        new_questionnaire_args: "Optional[NewQuestionnaireArguments]" = None,
        model_training_options: "Optional[Union[str, AnyDict]]" = None,
        model_type: "Optional[str]" = None,
        blueprint_id: "Optional[int]" = None,
    ):
        if labelset_column_id is not None and new_labelset_args is not None:
            raise IndicoInputError(
                "Cannot define both labelset_column_id and new_labelset_args, must be one "
                "or the other."
            )
        if (
            labelset_column_id is None and new_labelset_args is None
        ) and blueprint_id is None:
            raise IndicoInputError(
                "Must define one of either labelset_column_id or new_labelset_args."
            )

        model_training_options_json: "Optional[str]" = None
        if model_training_options:
            if isinstance(model_training_options, dict):
                model_training_options_json = jsons.dumps(model_training_options)
            else:
                model_training_options_json = model_training_options

        super().__init__(
            self.query,
            variables={
                "workflowId": workflow_id,
                "name": name,
                "datasetId": dataset_id,
                "sourceColumnId": source_column_id,
                "labelsetColumnId": labelset_column_id,
                "afterComponentId": after_component_id,
                "afterLinkId": after_link_id,
                "modelTrainingOptions": model_training_options_json,
                "modelType": model_type,
                "newLabelsetArgs": (
                    self.__labelset_to_json(new_labelset_args)
                    if new_labelset_args is not None
                    else None
                ),
                "questionnaireArgs": (
                    self.__questionnaire_to_json(new_questionnaire_args)
                    if new_questionnaire_args is not None
                    else None
                ),
                **({"blueprintId": blueprint_id} if blueprint_id else {}),
            },
        )

    def __labelset_to_json(self, labelset: "NewLabelsetArguments") -> "AnyDict":
        return {
            "name": labelset.name,
            "numLabelersRequired": labelset.num_labelers_required,
            "datacolumnId": labelset.datacolumn_id,
            "taskType": labelset.task_type.name,
            "targetNames": labelset.target_names,
            "fieldData": labelset.field_data,
        }

    def __questionnaire_to_json(
        self, questionnaire: "NewQuestionnaireArguments"
    ) -> "AnyDict":
        return {
            "instructions": questionnaire.instructions,
            "forceTextMode": questionnaire.force_text_mode,
            "showPredictions": questionnaire.show_predictions,
            "users": questionnaire.users,
        }

    def process_response(self, response: "Payload") -> "Workflow":
        return Workflow(
            **super().parse_payload(response)["addModelGroupComponent"]["workflow"]
        )


class DeleteWorkflowComponent(GraphQLRequest["Workflow"]):
    """
    Deletes a component from a workflow. If the component has an associated model, the model is deleted as well.
    Available on 5.3+ only.
    Returns workflow with updated list of components and links

    Args:
        workflow_id(int): the id of the workflow to delete the component from.
        component_id(int): the id of the component to delete.
    """

    query = """
        mutation deleteWorkflowComponent(
            $workflowId: Int!,
            $componentId: Int!
        ){
            deleteWorkflowComponent(
                workflowId: $workflowId,
                componentId: $componentId
            ){
                workflow {
                    id
                    components {
                        id
                        componentType
                        reviewable
                        filteredClasses
                        ... on ContentLengthComponent {
                            minimum
                            maximum
                        }
                        ... on ModelGroupComponent {
                            taskType
                            modelType
                            modelGroup {
                                status
                                id
                                name
                                taskType
                                questionnaireId
                                selectedModel{
                                    id
                                }
                            }
                        }

                    }
                    componentLinks {
                        id
                        headComponentId
                        tailComponentId
                        filters {
                            classes
                        }
                    }
                }
            }
        }
    """

    def __init__(self, workflow_id: int, component_id: int):
        super().__init__(
            self.query,
            variables={"workflowId": workflow_id, "componentId": component_id},
        )

    def process_response(self, response: "Payload") -> "Workflow":
        return Workflow(
            **super().parse_payload(response)["deleteWorkflowComponent"]["workflow"]
        )


class AddStaticModelComponent(RequestChain["Workflow"]):
    """
    Add a static model component to a workflow.

    Available on 6.14+ only.

    Args:
        `workflow_id(int)`: the id of the workflow to add the component to.
        `after_component_id(int)`: the id of the component to add this component after. Should be after the input ocr extraction component.
        `after_component_link_id(int)`: the component link to add this component after.
        `static_component_config(dict[str, Any])`: the configuration for the static model component. this would the dictionary returned from the job upon completion.
        `auto_process(bool)`: if True, the static model export will be automatically processed after it is uploaded.
        `export_file(str)`: the path to the static model export file.
    """

    previous: "Any" = None

    def __init__(
        self,
        workflow_id: int,
        after_component_id: "Optional[int]" = None,
        after_component_link_id: "Optional[int]" = None,
        static_component_config: "Optional[AnyDict]" = None,
        component_name: "Optional[str]" = None,
        auto_process: bool = False,
        export_file: "Optional[str]" = None,
    ):
        if not export_file and auto_process:
            raise IndicoInputError("Must provide export_file if auto_process is True.")

        if not auto_process and not static_component_config:
            raise IndicoInputError(
                "Must provide static_component_config if auto_process is False."
            )

        if not after_component_id and not after_component_link_id:
            raise IndicoInputError(
                "Must provide either `after_component_id` or `after_component_link_id`."
            )

        self.workflow_id = workflow_id
        self.after_component_id = after_component_id
        self.after_component_link_id = after_component_link_id
        self.component = {
            "component_type": "static_model",
            "config": {
                "export_meta": static_component_config,
            },
        }

        if component_name:
            self.component.update({"name": component_name})

        self.auto_process = auto_process
        self.export_file = export_file

    def requests(
        self,
    ) -> "Iterator[Union[UploadStaticModelExport, _AddWorkflowComponent]]":
        if self.auto_process:
            yield UploadStaticModelExport(
                auto_process=True,
                file_path=cast(str, self.export_file),
                workflow_id=self.workflow_id,
            )
            self.component.update(
                {
                    "config": {
                        "export_meta": self.previous.result,
                    }
                }
            )

        yield _AddWorkflowComponent(
            after_component_id=self.after_component_id,
            after_component_link=self.after_component_link_id,
            workflow_id=self.workflow_id,
            component=self.component,
        )


class ValidateComponentUpdate(GraphQLRequest["ComponentValidationResult"]):
    """
    Validate a component update before applying it.
    Returns information about components that will be deleted, links that will be
    removed/updated/added as a result of the update.

    Args:
        component_id(int): the id of the component to validate.
        workflow_id(int): the id of the workflow containing the component.
        component(dict): the component data with config to validate.

    Returns:
        ComponentValidationResult: validation result containing:
            - valid: whether the update is valid
            - components_to_delete: list of components that will be deleted
            - links_to_remove: list of links that will be removed
            - links_to_update: list of links that will be updated
            - links_to_add: list of links that will be added
    """

    query = """
        query validateComponentUpdate(
            $componentId: Int!,
            $workflowId: Int!,
            $component: JSONString!
        ) {
            validateComponentUpdate(
                componentId: $componentId,
                workflowId: $workflowId,
                component: $component
            ) {
                valid
                componentsToDelete {
                    id
                    name
                    componentType
                    modelGroupName
                    reason
                }
                linksToRemove {
                    id
                    headId
                    tailId
                    config
                }
                linksToUpdate {
                    id
                    headId
                    tailId
                    config
                }
                linksToAdd {
                    headId
                    tailId
                    config
                }
            }
        }
    """

    def __init__(
        self,
        component_id: int,
        workflow_id: int,
        component: "AnyDict",
    ):
        super().__init__(
            self.query,
            variables={
                "componentId": component_id,
                "workflowId": workflow_id,
                "component": jsons.dumps(component),
            },
        )

    def process_response(self, response: "Payload") -> "ComponentValidationResult":
        return ComponentValidationResult(
            **super().parse_payload(response)["validateComponentUpdate"]
        )


class _UpdateComponent(GraphQLRequest["Workflow"]):
    query = """
        mutation updateComponent(
            $componentId: Int!,
            $workflowId: Int!,
            $component: JSONString!
        ) {
            updateComponent(
                componentId: $componentId,
                workflowId: $workflowId,
                component: $component
            ) {
                workflow {
                    id
                    name
                    status
                    reviewEnabled
                    autoReviewEnabled
                    createdAt
                    createdBy
                    submissionRunnable
                    components {
                        id
                        componentType
                        reviewable
                        filteredClasses
                        ... on ContentLengthComponent {
                            minimum
                            maximum
                        }
                        ... on ModelGroupComponent {
                            taskType
                            modelType
                            modelGroup {
                                status
                                id
                                name
                                taskType
                                questionnaireId
                                classNames
                                selectedModel {
                                    id
                                }
                            }
                        }
                    }
                    componentLinks {
                        id
                        headComponentId
                        tailComponentId
                        config
                        filters {
                            classes
                        }
                    }
                    datasetId
                }
            }
        }
    """

    def __init__(
        self,
        component_id: int,
        workflow_id: int,
        component: "AnyDict",
    ):
        super().__init__(
            self.query,
            variables={
                "componentId": component_id,
                "workflowId": workflow_id,
                "component": jsons.dumps(component),
            },
        )

    def process_response(self, response: "Payload") -> "Workflow":
        return Workflow(
            **super().parse_payload(response)["updateComponent"]["workflow"]
        )


class UpdateComponent(RequestChain["Workflow"]):
    """
    Update a component in a workflow.

    Args:
        component_id(int): the id of the component to update.
        workflow_id(int): the id of the workflow containing the component.
        component(dict): the component data with config to update.
        auto_validate(bool): if True, validates the update first and raises
            IndicoInputError if validation fails. Defaults to False.

    Returns:
        Workflow: the updated workflow.
    """

    previous: "Any" = None

    def __init__(
        self,
        component_id: int,
        workflow_id: int,
        component: "AnyDict",
        auto_validate: bool = True,
    ):
        self.component_id = component_id
        self.workflow_id = workflow_id
        self.component = component
        self.auto_validate = auto_validate

    def requests(
        self,
    ) -> "Iterator[Union[ValidateComponentUpdate, _UpdateComponent]]":
        if self.auto_validate:
            yield ValidateComponentUpdate(
                component_id=self.component_id,
                workflow_id=self.workflow_id,
                component=self.component,
            )
            if not self.previous.valid:
                raise IndicoInputError(
                    "Component update validation failed. "
                    f"Components to delete: {len(self.previous.components_to_delete)}, "
                    f"Links to remove: {len(self.previous.links_to_remove)}, "
                    f"Links to update: {len(self.previous.links_to_update)}, "
                    f"Links to add: {len(self.previous.links_to_add)}"
                )

        yield _UpdateComponent(
            component_id=self.component_id,
            workflow_id=self.workflow_id,
            component=self.component,
        )
