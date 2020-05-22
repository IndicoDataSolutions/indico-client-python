import time
import pytest
from pathlib import Path
from indico.client import IndicoClient
from indico.queries.teach_tasks import CreateDatasetTeach
from indico.types.dataset import Dataset


def test_create_dataset_teach(indico):
    client = IndicoClient()
    datasets_dir = Path(__file__).parents[1] / "data"
    csv_path = datasets_dir / "staffer_large.csv"
    files = [str(datasets_dir / f"pdf{f}.pdf") for f in range(3)]

    response = client.call(
        CreateDatasetTeach(
            name=f"CreateDatasetTeach-test-{int(time.time())}",
            files=files,
            csv_path=str(csv_path),
        )
    )

    assert isinstance(response, Dataset)
    assert response.status == "COMPLETE"
    assert isinstance(response.id, int)
