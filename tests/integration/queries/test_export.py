import json
import re
from unittest import mock

import pytest

from indico.client import IndicoClient
from indico.errors import IndicoRequestError
from indico.queries.export import CreateExport, DownloadExport
from indico.types.dataset import Dataset
from indico.types.export import Export

from ..data.datasets import airlines_dataset


def test_create_and_download_export(airlines_dataset: Dataset):
    client = IndicoClient()
    export = client.call(
        CreateExport(
            dataset_id=airlines_dataset.id,
            labelset_id=airlines_dataset.labelsets[0].id,
            wait=True,
        )
    )
    assert export.status == "COMPLETE"
    csv = client.call(DownloadExport(export.id))
    assert all(c in csv.columns.to_list() for c in ["Target_1", "Text"])
    assert any(re.match("Indico_Id_[0-9]+", c) for c in csv.columns.to_list())
    assert csv["Text"][0] == "Your service is so bad."
    label = json.loads(csv["Target_1"][0])
    assert (
        label["targets"][0]["label"]
        == "You are threatening to never to use this airline again"
    )


def test_download_incomplete(indico):
    client = IndicoClient()
    export = Export()
    export.status = "FAILED"
    with pytest.raises(IndicoRequestError) as e:
        client.call(DownloadExport(export=export))
        assert isinstance(e._excinfo, IndicoRequestError)


def test_create_export_no_wait(airlines_dataset: Dataset):
    client = IndicoClient()
    export = client.call(
        CreateExport(
            dataset_id=airlines_dataset.id,
            labelset_id=airlines_dataset.labelsets[0].id,
            wait=False,
        )
    )
    assert export.status == "STARTED"
