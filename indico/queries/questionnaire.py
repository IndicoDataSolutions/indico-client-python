import json
from typing import Any, List, Optional

import deprecation

from indico.client.request import Delay, GraphQLRequest, RequestChain
from indico.errors import IndicoError, IndicoInputError, IndicoNotFound
from indico.queries import AddModelGroupComponent
from indico.queries.datasets import CreateDataset, GetDataset
from indico.types import (
    ModelTaskType,
    NewLabelsetArguments,
    NewQuestionnaireArguments,
    Workflow,
)
from indico.types.dataset import Dataset
from indico.types.questionnaire import Example, Questionnaire


class AddLabels(GraphQLRequest):
    """
    Add labels to an existing labelset.

    Args:
        dataset_id (int): Deprecated - The id of the dataset to add labels to.
        labelset_id (int): The id of the labelset to add labels to.
        labels (List(dict)): A list of dicts containing rowIndex and target fields for the data points to add.

    Raises:
        IndicoInputError if the length of targets and row_index are not equal

    """

    query = """
        mutation(
            $labels: [LabelInput]!,
            $labelset_id: Int!,
        ){
            submitLabelsV2(
                labels: $labels
                labelsetId: $labelset_id,
            ){ success }
        }
        """

    def __init__(
        self,
        labelset_id: int,
        labels: List[dict],
        model_group_id: int = None,
        dataset_id: int = None,
    ):
        super().__init__(
            query=self.query,
            variables={
                "labels": labels,
                "labelset_id": labelset_id,
                "model_group_id": None,
            },
        )


class GetQuestionnaireExamples(GraphQLRequest):
    """
    Gets unlabeled examples from a Questionnaire.

    Args:
        questionnaire_id (int): The id of the questionnaire to get examples from.
        num_examples (int): The number of examples to get from the questionnaire.

    Returns:
        List[Example]

    """

    query = """
    query(
        $questionnaire_id: Int!,
        $num_examples: Int!,
        $datafile_id: Int
    )
    {
        questionnaires(questionnaireIds: [$questionnaire_id]) {
            questionnaires {
                examples(numExamples: $num_examples, datafileId: $datafile_id) {
                    rowIndex
                    datafileId
                    source
                    id
                }
            }
        }
    }
    """

    def __init__(
        self,
        questionnaire_id: int,
        num_examples: int,
        datafile_id: Optional[int] = None,
    ):
        super().__init__(
            query=self.query,
            variables={
                "questionnaire_id": questionnaire_id,
                "num_examples": num_examples,
                "datafile_id": datafile_id,
            },
        )

    def process_response(self, response):
        try:
            examples = [
                Example(**e)
                for e in super().process_response(response)["questionnaires"][
                    "questionnaires"
                ][0]["examples"]
            ]
        except IndexError:
            raise IndicoNotFound(
                "Examples not found. Please check the ID you are using."
            )
        return examples


class GetQuestionnaire(GraphQLRequest):
    """
    Gets a questionnaire from an ID.

    Args:
        questionaire_id (int): The id of the questionnaire to get examples from.

    Returns
        Questionnaire
    """

    query = """
    query(
        $questionnaire_id: Int!
    )
    {
        questionnaires(questionnaireIds: [$questionnaire_id]) {
            questionnaires {
                id
                questionsStatus
                odl
                name
                numTotalExamples
                numFullyLabeled
                question {
                    labelset{
                        targetNames{
                            id
                            name
                        }
                    }
                }
            }
        }
    }
    """

    def __init__(self, questionnaire_id: int):
        super().__init__(
            query=self.query,
            variables={"questionnaire_id": questionnaire_id},
        )

    def process_response(self, response):
        questionnaire_list = super().process_response(response)["questionnaires"][
            "questionnaires"
        ]
        if not questionnaire_list or not questionnaire_list[0]:
            raise IndicoError("Cannot find questionnaire")
        return Questionnaire(**questionnaire_list[0])
