import json
from typing import List, Any

import pandas as pd

from indico.queries.datasets import CreateDataset, GetDataset

from indico.client.request import (
    GraphQLRequest,
    RequestChain,
)

from indico.types.questionnaire import Questionnaire, Example
from indico.errors import IndicoNotFound


class DataFileName(GraphQLRequest):
    query = """
    query(
        $datafileids: [Int]!
    ) {
        datafiles(datafileIds: $datafileids) {
            id
            name
        }
    }
    """

    def __init__(self, datafile_ids):
        super().__init__(
            query=self.query, variables={"datafileids": datafile_ids},
        )


class AddLabels(GraphQLRequest):
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

    def __init__(self, target, dataset_id, row_index, labelset_id):
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

    def __init__(self, name: str, dataset_id: int, source_column_id: int, targets: Any):
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


class _GetDatasetInfo(GraphQLRequest):
    query = """
        query(
            $id: Int!
        ) {
            dataset(id: $id) {
                files {
                    name
                }
            }
        }

    """

    def __init__(self, dataset_id: int):
        super().__init__(
            query=self.query, variables={"id": dataset_id},
        )


class GetDatasetInfo(RequestChain):
    previous = None

    def __init__(self, id: int):
        self.id = id
        super().__init__()

    def requests(self):
        yield _GetDatasetInfo(self.id)


class CreateDatasetTeach(RequestChain):
    previous = None

    def __init__(
        self, name: str, files: List[str], csv_path: str, batch_size: int = 20,
    ):
        csv = pd.read_csv(csv_path)
        self.files = files
        self.data = {
            fn: json.loads(label) for fn, label in zip(csv["text"], csv["labels"])
        }
        self.targets = list(
            set(t["label"] for sample in self.data.values() for t in sample)
        )
        self.name = name
        self.batch_size = batch_size
        super().__init__()

    def requests(self):
        yield CreateDataset(
            name=self.name, files=self.files, wait=True, batch_size=self.batch_size
        )
        dataset_id = self.previous.id
        yield CreateQuestionaire(
            name=self.name,
            dataset_id=dataset_id,
            source_column_id=self.previous.datacolumns[0].id,
            targets=self.targets,
        )
        questionaire_id = self.previous.id
        yield GetDataset(id=dataset_id)
        labelset_id = self.previous.labelsets[0].id
        yield GetQuestionaireExamples(
            questionaire_id=questionaire_id, num_examples=len(self.files)
        )
        yield AddLabels(
            target=[self.data.get(f.source) for f in self.previous],
            dataset_id=dataset_id,
            row_index=[d.row_index for d in self.previous],
            labelset_id=labelset_id,
        )

        yield GetDataset(id=dataset_id)
