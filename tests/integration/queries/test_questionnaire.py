import time
import pytest
import json
from pathlib import Path

import pandas as pd

from indico.client import IndicoClient
from indico.queries.datasets import CreateDataset
from indico.queries.questionnaire import CreateQuestionaire
from indico.types.questionnaire import Questionnaire


def test_create_questionnaire_no_labels(indico):
    client = IndicoClient()
    datasets_dir = Path(__file__).parents[1] / "data"
    files = [str(datasets_dir / f"pdf{f}.pdf") for f in range(3)]

    dataset = client.call(
        CreateDataset(name=f"CreateDataset-test-{int(time.time())}", files=files)
    )

    response = client.call(
        CreateQuestionaire(
            name=f"CreateDatasetTeach-test-{int(time.time())}",
            dataset_id=dataset.id,
            targets=["A", "B", "C"],
        )
    )

    assert isinstance(response, Questionnaire)


def test_create_questionnaire_labeled(indico):
    client = IndicoClient()
    datasets_dir = Path(__file__).parents[1] / "data"
    csv_path = datasets_dir / "staffer_large.csv"
    files = [str(datasets_dir / f"pdf{f}.pdf") for f in range(3)]

    dataset = client.call(
        CreateDataset(name=f"CreateDataset-test-{int(time.time())}", files=files)
    )

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
        )
    )

    assert isinstance(response, Questionnaire)
