import pytest
from indico.client import IndicoClient
from indico.types.dataset import Dataset
from indico.errors import IndicoRequestError
from indico.queries.export import CreateExport, _CreateExport, DownloadExport
from ..data.datasets import airlines_dataset


def test_create_and_download_export(airlines_dataset: Dataset):
    client = IndicoClient()
    export = client.call(CreateExport(dataset_id=airlines_dataset.id, wait=True))
    assert export.status == "COMPLETE"

    csv = client.call(DownloadExport(export.id))

    assert csv.columns.to_list() == ["row_index", "ID", "Target_1", "Text"]
    assert csv["Text"][0] == "Your service is so bad."
    assert (
        csv["Target_1"][0] == "You are threatening to never to use this airline again"
    )


def test_create_export_no_wait(airlines_dataset: Dataset):
    client = IndicoClient()
    export = client.call(CreateExport(dataset_id=airlines_dataset.id, wait=False))
    assert export.status == "STARTED"


def test_download_incomplete(airlines_dataset: Dataset):
    client = IndicoClient()
    export = client.call(CreateExport(dataset_id=airlines_dataset.id, wait=False))
    assert export.status == "STARTED"

    with pytest.raises(IndicoRequestError) as e:
        client.call(DownloadExport(export.id))
        assert isinstance(e._excinfo, IndicoRequestError)
