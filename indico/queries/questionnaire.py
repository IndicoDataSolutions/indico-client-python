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


@deprecation.deprecated(
    deprecated_in="5.0", details="Use AddModelGroupComponent instead"
)
class CreateQuestionaire(RequestChain):
    """
    Creates a labeled questionaire (teach task) for a dataset.

    Args:
        name (str): The name of the questionnaire.
        targets (set): A set containing the classes/label options for the task.
        dataset_id (int): Id for a dataset to create the questionnaire from.
        target_lookup (dict): An optional dict mapping sample text to labels.
        task_type (str): The type of the task. Defaults to ANNOTATION.
        data_type (str): The type of the data. Defaults to TEXT.
        workflow_id (int): The id of the workflow associated with the dataset.

    Returns:
        Questionnaire object
    """

    previous = None

    def __init__(
        self,
        name: str,
        targets: set,
        dataset_id: Dataset,
        workflow_id: int,
        after_component_id: int,
        target_lookup: dict = None,
        task_type: str = "ANNOTATION",
        data_type: str = "TEXT",
    ):
        self.dataset_id = dataset_id
        self.target_lookup = target_lookup
        self.targets = list(targets)
        self.name = name
        self.task_type = task_type
        self.data_type = data_type
        self.workflow_id = (workflow_id,)
        self.after_component_id = after_component_id
        super().__init__()

    def requests(self):
        yield GetDataset(id=self.dataset_id)
        new_labelset_args = NewLabelsetArguments(
            datacolumn_id=self.previous.datacolumns[0].id,
            name=self.name,
            task_type=next(v for v in ModelTaskType if v.name == self.task_type),
            target_names=self.targets,
        )
        yield AddModelGroupComponent(
            workflow_id=self.workflow_id[0],
            source_column_id=self.previous.datacolumns[0].id,
            new_labelset_args=new_labelset_args,
            dataset_id=self.dataset_id,
            name=self.name,
            after_component_id=self.after_component_id,
        )
        result: Workflow = self.previous
        questionaire_id = result.model_group_by_name(
            self.name
        ).model_group.questionnaire_id
        yield GetQuestionnaire(questionaire_id)
        status = self.previous.questions_status
        while status == "STARTED":
            yield Delay()
            yield GetQuestionnaire(questionaire_id)
            status = self.previous.questions_status

        if status == "FAILED":
            raise IndicoError("Creating the questionnaire has failed.")
        assert status == "COMPLETE"

        if self.target_lookup:
            num_examples = self.previous.num_total_examples
            yield GetDataset(id=self.dataset_id)
            labelset_id = self.previous.labelsets[0].id
            yield GetQuestionnaireExamples(
                questionnaire_id=questionaire_id, num_examples=num_examples
            )

            labels = []
            for f in self.previous:
                label = self.target_lookup.get(f.source)
                if label is not None:
                    labels.append(
                        {"rowIndex": f.row_index, "target": json.dumps(label)}
                    )

            if labels:
                yield AddLabels(
                    dataset_id=self.dataset_id,
                    labelset_id=labelset_id,
                    labels=labels,
                )
        yield GetQuestionnaire(questionaire_id)
