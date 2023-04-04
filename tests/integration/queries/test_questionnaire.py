import time
import pytest
import json
from pathlib import Path

import pandas as pd

from indico.client import IndicoClient
from indico.queries import CreateWorkflow
from indico.queries.datasets import CreateDataset, GetDataset
from indico.queries.questionnaire import (
    CreateQuestionaire,
    GetQuestionnaire,
    GetQuestionnaireExamples,
    AddLabels,
)
from indico.errors import IndicoError
from indico.types import Workflow
from indico.types.questionnaire import Questionnaire, Example


@pytest.fixture
def unlabeled_questionnaire(indico):
    client = IndicoClient()
    datasets_dir = Path(__file__).parents[1] / "data"
    files = [str(datasets_dir / f"pdf{f}.pdf") for f in range(3)]

    dataset = client.call(
        CreateDataset(name=f"CreateDataset-test-{int(time.time())}", files=files)
    )
    workflow: Workflow = client.call(CreateWorkflow(name=f"CreateWorkflow-test{int(time.time())}", dataset_id=dataset.id))
    after_component = workflow.component_by_type("INPUT_OCR_EXTRACTION").id

    questionnaire = client.call(
        CreateQuestionaire(
            name=f"CreateDatasetTeach-test-{int(time.time())}",
            dataset_id=dataset.id,
            targets=["A", "B", "C"],
            workflow_id=workflow.id,
            after_component_id=after_component
        )
    )
    return {"dataset": dataset, "questionnaire": questionnaire}


def test_create_questionnaire_no_labels(unlabeled_questionnaire):
    assert isinstance(unlabeled_questionnaire["questionnaire"], Questionnaire)


def test_create_questionnaire_labeled(indico):
    client = IndicoClient()
    datasets_dir = Path(__file__).parents[1] / "data"
    csv_path = datasets_dir / "staffer_large.csv"
    files = [str(datasets_dir / f"pdf{f}.pdf") for f in range(3)]

    dataset = client.call(
        CreateDataset(name=f"CreateDataset-test-{int(time.time())}", files=files)
    )
    workflow: Workflow = client.call(CreateWorkflow(name=f"CreateWorkflow-test{int(time.time())}", dataset_id=dataset.id))
    after_component = workflow.component_by_type("INPUT_OCR_EXTRACTION").id
    csv = pd.read_csv(csv_path)
    data = {
        string: json.loads(label) for string, label in zip(csv["text"], csv["labels"])
    }
    targets = list(set(t["label"] for sample in data.values() for t in sample))

    response = client.call(
        CreateQuestionaire(
            name=f"CreateDatasetTeach-test-{int(time.time())}",
            dataset_id=dataset.id,
            target_lookup=data,
            targets=targets,
            workflow_id=workflow.id,
            after_component_id=after_component
        )
    )

    assert isinstance(response, Questionnaire)

@pytest.mark.skip(reason="functionality is deprecated")
def test_get_nonexistent_questionnaire(indico):
    client = IndicoClient()
    with pytest.raises(IndicoError):
        client.call(GetQuestionnaire(123454321))


def test_get_questionnaire(indico, unlabeled_questionnaire):
    client = IndicoClient()
    response = client.call(
        GetQuestionnaire(unlabeled_questionnaire["questionnaire"].id)
    )
    assert isinstance(response, Questionnaire)
    assert response.id == unlabeled_questionnaire["questionnaire"].id
    assert not response.odl
    assert response.num_total_examples == 3
    assert response.num_fully_labeled == 0


def test_get_examples(indico, unlabeled_questionnaire):
    client = IndicoClient()
    examples = client.call(
        GetQuestionnaireExamples(
            questionnaire_id=unlabeled_questionnaire["questionnaire"].id, num_examples=3
        )
    )
    assert len(examples) == 3
    for example in examples:
        assert isinstance(example, Example)
        assert isinstance(example.source, str)
        assert isinstance(example.row_index, int)
        assert isinstance(example.datafile_id, int)


def test_add_labels(indico, unlabeled_questionnaire):
    client = IndicoClient()
    example = client.call(
        GetQuestionnaireExamples(
            questionnaire_id=unlabeled_questionnaire["questionnaire"].id, num_examples=1
        )
    )
    labels = [
        {
            "rowIndex": example[0].row_index,
            "target": json.dumps([{"start": 0, "end": 10, "label": "A"}]),
        }
    ]
    dataset_id = unlabeled_questionnaire["dataset"].id
    dataset = client.call(GetDataset(id=dataset_id))
    labelset_id = dataset.labelsets[0].id

    client.call(
        AddLabels(
            labelset_id=labelset_id,
            dataset_id=dataset_id,
            labels=labels,
        )
    )
    questionnaire = client.call(
        GetQuestionnaire(unlabeled_questionnaire["questionnaire"].id)
    )
    assert questionnaire.num_total_examples == 3
    assert questionnaire.num_fully_labeled == 1
