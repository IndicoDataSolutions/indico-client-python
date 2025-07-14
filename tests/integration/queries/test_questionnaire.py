import json
import time
from pathlib import Path

import pandas as pd
import pytest

from indico.client import IndicoClient
from indico.errors import IndicoError
from indico.queries import AddModelGroupComponent, CreateWorkflow
from indico.queries.datasets import CreateDataset, GetDataset
from indico.queries.questionnaire import (
    AddLabels,
    GetQuestionnaire,
    GetQuestionnaireExamples,
)
from indico.types import ModelTaskType, NewLabelsetArguments, Workflow
from indico.types.questionnaire import Example, Questionnaire


@pytest.fixture
def unlabeled_questionnaire(indico):
    client = IndicoClient()
    datasets_dir = Path(__file__).parents[1] / "data"
    files = [str(datasets_dir / f"pdf{f}.pdf") for f in range(3)]

    dataset = client.call(
        CreateDataset(name=f"CreateDataset-test-{int(time.time())}", files=files)
    )
    workflow: Workflow = client.call(
        CreateWorkflow(
            name=f"CreateWorkflow-test{int(time.time())}", dataset_id=dataset.id
        )
    )
    after_component_id = workflow.component_by_type("INPUT_OCR_EXTRACTION").id
    source_col_id = dataset.datacolumn_by_name("text").id
    classifier_name = f"CreateDatasetTeach-test-{int(time.time())}"

    new_labelset_args = {
        "datacolumn_id": source_col_id,
        "name": classifier_name,
        "num_labelers_required": 1,
        "task_type": ModelTaskType.CLASSIFICATION,
        "target_names": ["A", "B", "C"],
    }

    questionnaire = client.call(
        AddModelGroupComponent(
            name=classifier_name,
            dataset_id=dataset.id,
            workflow_id=workflow.id,
            new_labelset_args=NewLabelsetArguments(**new_labelset_args),
            source_column_id=source_col_id,
            after_component_id=after_component_id,
        )
    )
    questionnaire_id = questionnaire.model_group_by_name(
        classifier_name
    ).model_group.questionnaire_id
    return {
        "dataset": dataset,
        "questionnaire_id": questionnaire_id,
    }


def test_create_questionnaire_no_labels(unlabeled_questionnaire):
    assert isinstance(unlabeled_questionnaire["questionnaire_id"], int)


def test_create_questionnaire_labeled(indico):
    client = IndicoClient()
    datasets_dir = Path(__file__).parents[1] / "data"
    csv_path = datasets_dir / "staffer_large.csv"
    files = [str(datasets_dir / f"pdf{f}.pdf") for f in range(3)]

    dataset = client.call(
        CreateDataset(name=f"CreateDataset-test-{int(time.time())}", files=files)
    )
    workflow: Workflow = client.call(
        CreateWorkflow(
            name=f"CreateWorkflow-test{int(time.time())}", dataset_id=dataset.id
        )
    )
    source_col_id = dataset.datacolumn_by_name("text").id
    after_component_id = workflow.component_by_type("INPUT_OCR_EXTRACTION").id
    csv = pd.read_csv(csv_path)
    data = {
        string: json.loads(label) for string, label in zip(csv["text"], csv["labels"])
    }
    classifier_name = f"CreateDatasetTeach-test-{int(time.time())}"
    targets = list(set(t["label"] for sample in data.values() for t in sample))
    new_labelset_args = {
        "datacolumn_id": source_col_id,
        "name": classifier_name,
        "num_labelers_required": 1,
        "task_type": ModelTaskType.CLASSIFICATION,
        "target_names": targets,
    }

    response = client.call(
        AddModelGroupComponent(
            name=classifier_name,
            dataset_id=dataset.id,
            workflow_id=workflow.id,
            new_labelset_args=NewLabelsetArguments(**new_labelset_args),
            source_column_id=source_col_id,
            after_component_id=after_component_id,
        )
    )

    assert isinstance(response, Workflow)


def test_get_nonexistent_questionnaire(indico):
    client = IndicoClient()
    with pytest.raises(IndicoError):
        client.call(GetQuestionnaire(123454321))


def test_get_questionnaire(indico, unlabeled_questionnaire):
    client = IndicoClient()
    response = client.call(
        GetQuestionnaire(unlabeled_questionnaire["questionnaire_id"])
    )
    assert isinstance(response, Questionnaire)
    assert response.id == unlabeled_questionnaire["questionnaire_id"]
    assert not response.odl
    assert response.num_total_examples == 3
    assert response.num_fully_labeled == 0


def test_get_examples(indico, unlabeled_questionnaire):
    client = IndicoClient()
    examples = client.call(
        GetQuestionnaireExamples(
            questionnaire_id=unlabeled_questionnaire["questionnaire_id"], num_examples=3
        )
    )
    assert len(examples) == 3
    for example in examples:
        assert isinstance(example, Example)
        assert isinstance(example.contexts, list)
        assert isinstance(example.datafile_ids, list)
        assert isinstance(example.original_datafile_id, int)
        assert isinstance(example.original_datafile_name, str)


def test_add_labels(indico, unlabeled_questionnaire):
    client = IndicoClient()
    questionnaire = client.call(
        GetQuestionnaire(questionnaire_id=unlabeled_questionnaire["questionnaire_id"])
    )
    targets = questionnaire.question.labelset.target_names
    example = client.call(
        GetQuestionnaireExamples(
            questionnaire_id=unlabeled_questionnaire["questionnaire_id"], num_examples=1
        )
    )
    targets = [
        {
            "clsId": next(t.id for t in targets if t.name == "A"),
            "spans": [{"start": 0, "end": 10, "pageNum": 0}],
        }
    ]
    labels = [
        {
            "exampleId": example[0].id,
            "targets": targets,
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
        GetQuestionnaire(unlabeled_questionnaire["questionnaire_id"])
    )
    assert questionnaire.num_total_examples == 3
    assert questionnaire.num_fully_labeled == 1
