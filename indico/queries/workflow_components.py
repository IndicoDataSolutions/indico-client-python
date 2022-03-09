import json
from typing import List

from indico import GraphQLRequest, RequestChain
from indico.errors import IndicoInputError
from indico.types import NewLabelsetArguments, NewQuestionnaireArguments, Workflow


class _AddWorkflowComponent(GraphQLRequest):
    query = """mutation addWorkflowComponent($afterComponentId:Int, $afterComponentLinkId: Int, $component: JSONString!, $workflowId: Int!){
  addWorkflowComponent(afterComponentId: $afterComponentId,
	component: $component,
  workflowId:$workflowId
  afterComponentLinkId: $afterComponentLinkId){
  workflow {
                id
                components {
                                id
                                componentType
                                reviewable
                                filteredClasses
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
                                    passed
                                }
                            }

            }
  }
}"""

    def __init__(
        self,
        after_component_id: int,
        after_component_link: int,
        workflow_id: int,
        component: str,
    ):
        super().__init__(
            self.query,
            variables={
                "afterComponentId": after_component_id,
                "afterComponentLink": after_component_link,
                "workflowId": workflow_id,
                "component": component,
            },
        )

    def process_response(self, response) -> Workflow:
        response = super().process_response(response)
        return Workflow(**response["addWorkflowComponent"]["workflow"])


class AddFilteredClassesComponent(RequestChain):
    previous = None

    def __init__(
        self,
        classes: List[List[str]],
        model_group_id: int,
        workflow_id: int,
        after_component_id: int = None,
        after_component_link_id: int = None,
    ):
        self.workflow_id = workflow_id
        self.classes = classes
        self.model_group_id = model_group_id
        self.after_component_id = after_component_id
        self.after_component_link_id = after_component_link_id
        self.component = {
            "component_type": "link_classification_model",
            "config": {"model_group_id": model_group_id, "filtered_classes": classes},
        }
        super().__init__()

    def requests(self):
        yield _AddWorkflowComponent(
            after_component_id=self.after_component_id,
            after_component_link=self.after_component_link_id,
            component=json.dumps(self.component),
            workflow_id=self.workflow_id,
        )


class AddContentLengthFilterComponent(RequestChain):
    def __init__(
        self,
        workflow_id: int,
        minimum: int = None,
        maximum: int = None,
        after_component_id: int = None,
        after_component_link_id: int = None,
    ):
        self.after_component_id = after_component_id
        self.after_component_link_id = after_component_link_id
        self.workflow_id = workflow_id
        self.minimum = minimum
        self.maximum = maximum
        self.component = {
            "component": {
                "component_type": "CONTENT_LENGTH",
                "config": {"minimum": minimum, "maximum": maximum},
            }
        }
        super().__init__()

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
            mutation addModelGroup(
          $workflowId: Int!, 
          $name: String!, 
          $datasetId: Int!, 
          $sourceColumnId: Int!, 
          $afterComponentId: Int, 
          $afterLinkId: Int,
          $labelsetColumnId: Int,
          $newLabelsetArgs: NewLabelsetInput,
          $questionnaireArgs: QuestionnaireInput,
          $modelTrainingOptions: JSONString,
          $modelType : ModelType
        ) {
          addModelGroupComponent(workflowId: $workflowId, name: $name, datasetId: $datasetId, 
          sourceColumnId: $sourceColumnId, afterComponentId: $afterComponentId, afterLinkId: $afterLinkId, labelsetColumnId: $labelsetColumnId,
          modelTrainingOptions: $modelTrainingOptions,

    newLabelsetArgs: $newLabelsetArgs,
    questionnaireArgs: $questionnaireArgs, modelType: $modelType) {
            workflow {
                id
                components {
                                id
                                componentType
                                reviewable

                                filteredClasses
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
                "newLabelsetArgs": self.__labelset_to_json(new_labelset_args)
                if new_labelset_args is not None
                else None,
                "questionnaireArgs": self.__questionnaire_to_json(
                    new_questionnaire_args
                )
                if new_questionnaire_args is not None
                else None,
            },
        )

    def __labelset_to_json(self, labelset: NewLabelsetArguments):
        return {
            "name": labelset.name,
            "numLabelersRequired": labelset.num_labelers_required,
            "datacolumnId": labelset.datacolumn_id,
            "taskType": labelset.task_type,
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

