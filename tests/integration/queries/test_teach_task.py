import time
import pytest
from pathlib import Path
from indico.client import IndicoClient
from indico.queries.datasets import CreateDataset
from indico.queries.teach_tasks import CreateTeachTask
from indico.types.dataset import Dataset


def test_create_dataset_teach(indico):
    client = IndicoClient()
    datasets_dir = Path(__file__).parents[1] / "data"
    csv_path = datasets_dir / "staffer_large.csv"
    files = [str(datasets_dir / f"pdf{f}.pdf") for f in range(3)]

    dataset = client.call(
        CreateDataset(
            name=f"CreateDataset-test-{int(time.time())}", files=files
        )
    )

    response = client.call(
        CreateTeachTask(
            name=f"CreateDatasetTeach-test-{int(time.time())}",
            csv_path=str(csv_path),
            dataset=dataset,
            num_examples=len(files)
        )
    )

    assert isinstance(response, Dataset)
    assert response.status == "COMPLETE"
    assert isinstance(response.id, int)
