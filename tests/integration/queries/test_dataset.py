import time
import pytest
from pathlib import Path
import os
from indico.client import IndicoClient
from indico.queries.datasets import (
    GetDataset,
    GetDatasetFileStatus,
    CreateDataset,
    ListDatasets,
)
from indico.types.dataset import Dataset
from indico.errors import IndicoRequestError
from tests.integration.data.datasets import airlines_dataset


def test_create_dataset(indico):
    client = IndicoClient()
    dataset_filepath = str(Path(__file__).parents[1]) + "/data/AirlineComplaints.csv"

    response = client.call(
        CreateDataset(
            name=f"AirlineComplaints-test-{int(time.time())}", files=[dataset_filepath]
        )
    )

    assert isinstance(response, Dataset)
    assert response.status == "COMPLETE"
    assert isinstance(response.id, int)


def test_get_datasets(indico, airlines_dataset):
    client = IndicoClient()
    dataset = client.call(GetDataset(id=airlines_dataset.id))

    assert isinstance(dataset, Dataset)
    assert dataset.id == airlines_dataset.id


def test_get_dataset_with_bad_id(indico):
    client = IndicoClient()

    with pytest.raises(IndicoRequestError):
        dataset = client.call(GetDataset(id=10000000))


def test_get_dataset_file_status(indico, airlines_dataset):
    client = IndicoClient()
    dataset = client.call(GetDatasetFileStatus(id=airlines_dataset.id))

    assert isinstance(dataset, Dataset)
    assert dataset.id == airlines_dataset.id
    assert len(dataset.files) > 0
    assert dataset.files[0].status != None


def test_list_datasets(indico, airlines_dataset):
    client = IndicoClient()
    datasets = client.call(ListDatasets(limit=1))

    assert isinstance(datasets, list)
    assert len(datasets) == 1
    assert type(datasets[0]) == Dataset


def test_images(indico):
    client = IndicoClient()

    dataset_filepath = str(Path(__file__).parents[1]) + "/data/dog_vs_cats_small.csv"
    response = client.call(
        CreateDataset(
            name=f"image-dataset-test-{int(time.time())}",
            files=dataset_filepath,
            from_local_images=True,
        )
    )
    assert isinstance(response, Dataset)
    assert response.status == "COMPLETE"
    assert isinstance(response.id, int)


def test_images_batch(indico):
    client = IndicoClient()

    dataset_filepath = str(Path(__file__).parents[1]) + "/data/dog_vs_cats_small.csv"
    response = client.call(
        CreateDataset(
            name=f"image-dataset-test-{int(time.time())}",
            files=dataset_filepath,
            from_local_images=True,
            batch_size=10,
        )
    )
    assert isinstance(response, Dataset)
    assert response.status == "COMPLETE"
    assert isinstance(response.id, int)


def test_upload_pdf_dataset_batch(indico):
    client = IndicoClient()
    file_names = ["mock.pdf", "mock_2.pdf", "mock_3.pdf"]
    parent_path = str(Path(__file__).parent.parent / "data")
    dataset_filepaths = [
        os.path.join(parent_path, file_name) for file_name in file_names
    ]
    dataset = client.call(
        CreateDataset(
            name=f"pdf-dataset-test-{int(time.time())}",
            files=dataset_filepaths,
            batch_size=1,
        )
    )
    assert isinstance(dataset, Dataset)
    assert dataset.status == "COMPLETE"
    assert isinstance(dataset.id, int)
    assert dataset.datacolumns[0].name == "text"
    response = client.call(GetDatasetFileStatus(id=dataset.id))
    for datafile in response.files:
        assert datafile.status == "PROCESSED"
        assert datafile.file_type == "pdf"
