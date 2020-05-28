import json
from typing import List, Any

import pandas as pd

from indico.queries.datasets import CreateDataset, GetDataset

from indico.client.request import (
    GraphQLRequest,
    RequestChain,
)

from indico.types.questionnaire import Questionnaire, Example
from indico.types.dataset import Dataset
from indico.errors import IndicoNotFound, IndicoInputError


class AddLabels(GraphQLRequest):
    """
    Add labels to an existing labelset.

    Args:
        dataset_id (int): The id of the dataset to add labels to.
        labelset_id (int): The id of the labelset to add labels to.
        target (List[Any]): A list of labels to add to the labelset.
        row_index (List[Any]): The row indices corresponding with each item in targets.

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
        self, dataset_id: int, labelset_id: int, target: List[Any], row_index: List[int]
    ):
        if len(target) != len(row_index):
            raise IndicoInputError("Mismatch in lengths between target and row_index.")

        labels = []
        for t, row_id in zip(target, row_index):
            if t is not None:
                labels.append({"rowIndex": row_id, "target": json.dumps(t)})
        super().__init__(
            query=self.query,
            variables={
                "labels": labels,
                "dataset_id": dataset_id,
                "labelset_id": labelset_id,
            },
        )


class GetQuestionaireExamples(GraphQLRequest):
    """
    Gets unlabeled examples from a Questionnaire.

    Args:
        questionaire_id (int): The id of the questionnaire to get examples from.
        num_examples (int): The number of examples to get from the questionaire.

    Returns:
        List[Example]

    """

    query = """
    query(
        $questionaire_id: Int!,
        $num_examples: Int!
    )
    {
        questionnaires(questionnaireIds: [$questionaire_id]) {
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

    def __init__(self, questionaire_id: int, num_examples: int):
        super().__init__(
            query=self.query,
            variables={
                "questionaire_id": questionaire_id,
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


class CreateQuestionaire(GraphQLRequest):
    """
    Creates the questionnaire (teach task) for a dataset.

    Args:
        name (str): The name of the questionnaire.
        dataset_id (int): The id of the dataset to create the questionnaire from.
        source_column_id (int): The id of the source column to create a questionnaire from.
        targets (List[str]): The classes for the dataset.

    Returns:
        Questionnaire

    """

    query = """
        mutation(
            $name: String!,
            $dataset_id: Int!,
            $questions: [QuestionInput]!,
            $source_col_id: Int!,
        ) {
            createQuestionnaire (
                datasetId: $dataset_id,
                dataType: TEXT,
                name: $name,
                numLabelersRequired: 1,
                questions: $questions,
                sourceColumnId: $source_col_id,
                instructions: ""
            ) {
                id
            }
        }
    """

    def __init__(
        self, name: str, dataset_id: int, source_column_id: int, targets: List[str]
    ):
        questions = [
            {"type": "ANNOTATION", "targets": targets, "keywords": [], "text": name,}
        ]
        super().__init__(
            query=self.query,
            variables={
                "name": name,
                "dataset_id": dataset_id,
                "questions": questions,
                "source_col_id": source_column_id,
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


class CreateTeachTask(RequestChain):
    """
    Creates a labeled questionaire (teach task) for a dataset.

    Args:
        name (str): The name of the questionnaire.
        csv_path (str): Path to a csv with columns containing text and json encoded labels.
        dataset (Dataset): Dataset to create the questionnaire from.
        num_examples (int): number of rows in the dataset in total.
        text_column (str): Optional. The column name in the csv containing the text.
        label_column (str): Optional. The column name in the csv containing the json encoded labels. 
        
    Returns:
        Dataset object   
    """

    previous = None

    def __init__(
        self,
        name: str,
        csv_path: str,
        dataset: Dataset,
        num_examples: int,
        text_column="text",
        label_column="labels",
    ):
        self.dataset_id = dataset.id
        self.dataset = dataset
        csv = pd.read_csv(csv_path)
        self.data = {
            fn: json.loads(label) for fn, label in zip(csv["text"], csv["labels"])
        }
        self.targets = list(
            set(t["label"] for sample in self.data.values() for t in sample)
        )
        self.name = name
        self.num_examples = num_examples
        super().__init__()

    def requests(self):
        yield CreateQuestionaire(
            name=self.name,
            dataset_id=self.dataset_id,
            source_column_id=self.dataset.datacolumns[0].id,
            targets=self.targets,
        )
        questionaire_id = self.previous.id
        yield GetDataset(id=self.dataset_id)
        labelset_id = self.previous.labelsets[0].id
        yield GetQuestionaireExamples(
            questionaire_id=questionaire_id, num_examples=self.num_examples
        )
        yield AddLabels(
            target=[self.data.get(f.source) for f in self.previous],
            dataset_id=self.dataset_id,
            row_index=[d.row_index for d in self.previous],
            labelset_id=labelset_id,
        )

        yield GetDataset(id=self.dataset_id)
