from typing import Any, List

import jsons
import requests

from indico import GraphQLRequest, RequestChain
from indico.errors import IndicoInputError, IndicoRequestError
from indico.types import (
    Job,
    LinkedLabelGroup,
    NewLabelsetArguments,
    NewQuestionnaireArguments,
    Workflow,
)
from indico.types.static_model import StaticModelConfig


class _AddWorkflowComponent(GraphQLRequest):
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
        after_component_id: int,
        after_component_link: int,
        workflow_id: int,
        component: dict,
        blueprint_id: int | None = None,
    ):
        super().__init__(
            self.query,
            variables={
                "afterComponentId": after_component_id,
                "afterComponentLink": after_component_link,
                "workflowId": workflow_id,
                "component": jsons.dumps(component),
                "blueprintId": blueprint_id,
            },
        )

    def process_response(self, response) -> Workflow:
        return Workflow(
            **super().process_response(response)["addWorkflowComponent"]["workflow"]
        )


class AddLinkedLabelComponent(RequestChain):
    """
    Adds a linked label transformer that groups together labels

    Args:
        after_component_id(int): the component this component follows.
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
        groups: List[LinkedLabelGroup],
        after_component_link_id: int = None,
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

    def __groups_to_json(self, group: LinkedLabelGroup):
        return {
            "name": group.name,
            "strategy": group.strategy.name.lower(),
            "class_names": group.class_ids,
            "strategy_settings": group.strategy_settings,
        }

    def requests(self):
        yield _AddWorkflowComponent(
            after_component_id=self.after_component_id,
            after_component_link=self.after_component_link_id,
            workflow_id=self.workflow_id,
            component=self.component,
        )


class AddContentLengthFilterComponent(RequestChain):
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
        after_component_link_id: int = None,
        minimum: int = None,
        maximum: int = None,
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

    def requests(self):
        yield _AddWorkflowComponent(
            after_component_id=self.after_component_id,
            after_component_link=self.after_component_link_id,
            workflow_id=self.workflow_id,
            component=self.component,
        )


class AddLinkClassificationComponent(RequestChain):
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
        filtered_classes: List[List[str]],
        labels: str = None,
        after_component_link_id: int = None,
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

    def requests(self):
        yield _AddWorkflowComponent(
            after_component_id=self.after_component_id,
            after_component_link=self.after_component_link_id,
            workflow_id=self.workflow_id,
            component=self.component,
        )


class AddModelGroupComponent(GraphQLRequest):
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

    """

    query = """
        mutation addModelGroup($workflowId: Int!, $name: String!, $datasetId: Int!, $sourceColumnId: Int!, $afterComponentId: Int, $labelsetColumnId: Int, $afterLinkId: Int, $newLabelsetArgs: NewLabelsetInput, $questionnaireArgs: QuestionnaireInput, $modelTrainingOptions: JSONString, $modelType: ModelType) {
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
        after_component_id: int = None,
        after_link_id: int = None,
        labelset_column_id: int = None,
        new_labelset_args: NewLabelsetArguments = None,
        new_questionnaire_args: NewQuestionnaireArguments = None,
        model_training_options: str = None,
        model_type: str = None,
    ):
        if labelset_column_id is not None and new_labelset_args is not None:
            raise IndicoInputError(
                "Cannot define both labelset_column_id and new_labelset_args, must be one "
                "or the other."
            )
        if labelset_column_id is None and new_labelset_args is None:
            raise IndicoInputError(
                "Must define one of either labelset_column_id or new_labelset_args."
            )

        if model_training_options:
            model_training_options = jsons.dumps(model_training_options)

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
                "modelTrainingOptions": model_training_options,
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
            },
        )

    def __labelset_to_json(self, labelset: NewLabelsetArguments):
        return {
            "name": labelset.name,
            "numLabelersRequired": labelset.num_labelers_required,
            "datacolumnId": labelset.datacolumn_id,
            "taskType": labelset.task_type.name,
            "targetNames": labelset.target_names,
        }

    def __questionnaire_to_json(self, questionnaire: NewQuestionnaireArguments):
        return {
            "instructions": questionnaire.instructions,
            "forceTextMode": questionnaire.force_text_mode,
            "showPredictions": questionnaire.show_predictions,
            "users": questionnaire.users,
        }

    def process_response(self, response) -> Workflow:
        return Workflow(
            **super().process_response(response)["addModelGroupComponent"]["workflow"]
        )


class DeleteWorkflowComponent(GraphQLRequest):
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

    def process_response(self, response) -> Workflow:
        return Workflow(
            **super().process_response(response)["deleteWorkflowComponent"]["workflow"]
        )


class AddStaticModelComponent(RequestChain):
    """
    Add a static model component to a workflow.
    Available on 6.13+ only.

    Args:
        workflow_id(int): the id of the workflow to add the component to.
        after_component_id(int): the id of the component to add this component after. Should be after the input ocr extraction component.
        static_component_config(dict[str, Any]): the configuration for the static model component.
    """

    def __init__(
        self,
        workflow_id: int,
        after_component_id: int,
        static_component_config: StaticModelConfig,
    ):
        self.workflow_id = workflow_id
        self.after_component_id = after_component_id
        self.component = {
            "component_type": "static_model",
            "config": static_component_config,
        }

    def requests(self):
        yield _AddWorkflowComponent(
            after_component_id=self.after_component_id,
            workflow_id=self.workflow_id,
            component=self.component,
            after_component_link=None,
        )


class ProcessStaticModelExport(GraphQLRequest):
    """
    Process a static model export.
    Available on 6.13+ only.

    Args:
        storage_uri(str): the storage uri of the static model export that was uploaded to Indico.

    Returns:
        Job: the job that was created to process the static model export.
    """

    query = """
        mutation processStaticModelExport($storageUri: String!) {
            processStaticModelExport(storageUri: $storageUri) {
                jobId
            }
        }
    """

    def __init__(self, storage_uri: str):
        super().__init__(self.query, variables={"storageUri": storage_uri})

    def process_response(self, response) -> Job:
        job_id = super().process_response(response)["processStaticModelExport"]["jobId"]
        return Job(id=job_id)


class UploadStaticModelExport(GraphQLRequest):
    """
    Upload a static model export to Indico.
    Available on 6.13+ only.

    Args:
        file_path(str): path to the export zip file to upload to Indico.

    Returns:
        str: the storage uri of the static model export.
    """

    query = """
        query exportUpload {
            exportUpload {
                signedUrl
                storageUri
            }
        }
    """

    def __init__(self, file_path: str):
        self.file_path = file_path
        super().__init__(self.query)

    def process_response(self, response) -> str:
        resp = super().process_response(response)["exportUpload"]
        signed_url = resp["signedUrl"]
        storage_uri = resp["storageUri"]

        with open(self.file_path, "rb") as file:
            file_content = file.read()

        headers = {"Content-Type": "application/zip"}
        response = requests.put(signed_url, data=file_content, headers=headers)

        if response.status_code != 200:
            raise IndicoRequestError(
                f"Failed to upload static model export: {response.text}"
            )

        return storage_uri
