import json
from typing import List, Any

import pandas as pd

from indico.queries.datasets import CreateDataset, GetDataset

from indico.client.request import (
    GraphQLRequest,
    RequestChain,
    Debouncer,
)

from indico.types.questionnaire import Questionnaire, Example
from indico.types.dataset import Dataset
from indico.errors import IndicoNotFound, IndicoInputError, IndicoError


class AddLabels(GraphQLRequest):
    """
    Add labels to an existing labelset.

    Args:
        dataset_id (int): The id of the dataset to add labels to.
        labelset_id (int): The id of the labelset to add labels to.
        labels (List(dict)): A list of dicts containing rowIndex and target fields for the data points to add.

    Raises:
        IndicoInputError if the length of targets and row_index are not equal

    """

    query = """
        mutation(
            $labels: [SubmissionLabel]!,
            $dataset_id: Int!,
            $labelset_id: Int!,
        ){
            submitLabels(
                datasetId: $dataset_id,
                labelsetId: $labelset_id,
                labels: $labels
            ){ success }
        }
        """

    def __init__(
        self, dataset_id: int, labelset_id: int, labels: List[dict],
    ):

        super().__init__(
            query=self.query,
            variables={
                "labels": labels,
                "dataset_id": dataset_id,
                "labelset_id": labelset_id,
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
        $num_examples: Int!
    )
    {
        questionnaires(questionnaireIds: [$questionnaire_id]) {
            questionnaires {
                examples(numExamples: $num_examples) {
                    rowIndex
                    datafileId
                    source
                }
            }
        }
    }
    """

    def __init__(self, questionnaire_id: int, num_examples: int):
        super().__init__(
            query=self.query,
            variables={
                "questionnaire_id": questionnaire_id,
                "num_examples": num_examples,
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
            }
        }
    }
    """

    def __init__(self, questionnaire_id: int):
        super().__init__(
            query=self.query, variables={"questionnaire_id": questionnaire_id},
        )

    def process_response(self, response):
        questionnaire_list = super().process_response(response)["questionnaires"]["questionnaires"]
        if not questionnaire_list:
            raise IndicoError("Cannot find questionnaire")
        return Questionnaire(
            **questionnaire_list[0]
        )


class _CreateQuestionaire(GraphQLRequest):
    """
    Creates the questionnaire (teach task) for a dataset.

    Args:
        name (str): The name of the questionnaire.
        dataset_id (int): The id of the dataset to create the questionnaire from.
        source_column_id (int): The id of the source column to create a questionnaire from.
        targets (List[str]): The classes for the dataset.
        task_type (str): The type of the task to create.
        data_type (str): The type of the source data.

    Returns:
        Questionnaire

    """

    query = """
        mutation(
            $name: String!,
            $dataset_id: Int!,
            $questions: [QuestionInput]!,
            $source_col_id: Int!,
            $data_type: DataType!,
        ) {
            createQuestionnaire (
                datasetId: $dataset_id,
                dataType: $data_type,
                name: $name,
                numLabelersRequired: 1,
                questions: $questions,
                sourceColumnId: $source_col_id,
                instructions: ""
            ) {
                id
                questionsStatus
                numTotalExamples
            }
        }
    """

    def __init__(
        self,
        name: str,
        dataset_id: int,
        source_column_id: int,
        targets: List[str],
        task_type: str,
        data_type: str,
    ):
        questions = [
            {"type": task_type, "targets": targets, "keywords": [], "text": name,}
        ]
        super().__init__(
            query=self.query,
            variables={
                "name": name,
                "dataset_id": dataset_id,
                "questions": questions,
                "source_col_id": source_column_id,
                "data_type": data_type,
            },
        )

    def process_response(self, response):
        try:
            questionnaire = Questionnaire(
                **super().process_response(response)["createQuestionnaire"]
            )
        except IndexError:
            raise IndicoNotFound("Failed to create Questionnaire")
        return questionnaire


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
        
    Returns:
        Questionnaire object   
    """

    previous = None

    def __init__(
        self,
        name: str,
        targets: set,
        dataset_id: Dataset,
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
        super().__init__()

    def requests(self):
        yield GetDataset(id=self.dataset_id)
        yield _CreateQuestionaire(
            name=self.name,
            dataset_id=self.dataset_id,
            source_column_id=self.previous.datacolumns[0].id,
            targets=self.targets,
            task_type=self.task_type,
            data_type=self.data_type,
        )
        questionaire_id = self.previous.id
        status = self.previous.questions_status
        debouncer = Debouncer()
        while status == "STARTED":
            debouncer.backoff()
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
                    dataset_id=self.dataset_id, labelset_id=labelset_id, labels=labels,
                )
        yield GetQuestionnaire(questionaire_id)
