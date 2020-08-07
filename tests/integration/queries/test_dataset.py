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
    DeleteDataset,
    CreateDataset_v2,
    AddFiles,
    ProcessFiles,
    ProcessCSV,
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


def test_upload_pdf_interrupt(indico):
    client = IndicoClient()

    client._http.request_session.cookies.clear()
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


def test_delete_dataset(indico):
    client = IndicoClient()
    dataset_filepath = str(Path(__file__).parents[1]) + "/data/AirlineComplaints.csv"

    dataset = client.call(
        CreateDataset(
            name=f"AirlineComplaints-test-{int(time.time())}", files=[dataset_filepath]
        )
    )

    assert isinstance(dataset, Dataset)
    assert dataset.status == "COMPLETE"
    assert isinstance(dataset.id, int)

    success = client.call(DeleteDataset(id=dataset.id))
    assert success == True

    with pytest.raises(IndicoRequestError):
        dataset = client.call(GetDataset(id=dataset.id))


#########################
## Dataset Pipeline v2 ##
#########################
def test_create_dataset_v2_from_files(indico):
    client = IndicoClient()

    dataset = client.call(CreateDataset_v2(name=f"dataset-{int(time.time())}"))

    file_names = ["mock.pdf", "mock_2.pdf", "mock_3.pdf"]
    parent_path = str(Path(__file__).parent.parent / "data")
    dataset_filepaths = [
        os.path.join(parent_path, file_name) for file_name in file_names
    ]

    dataset = client.call(AddFiles(dataset_id=dataset.id, files=dataset_filepaths))

    for f in dataset.files:
        assert f.status == "DOWNLOADED"

    datafile_ids = [f.id for f in dataset.files]

    dataset = client.call(
        ProcessFiles(dataset_id=dataset.id, datafile_ids=datafile_ids, wait=True)
    )


def test_create_dataset_v2_from_csv(indico):
    client = IndicoClient()
    dataset = client.call(CreateDataset_v2(name=f"dataset-{int(time.time())}"))
    dataset_filepath = str(Path(__file__).parents[1]) + "/data/AirlineComplaints.csv"
    dataset = client.call(AddFiles(dataset_id=dataset.id, files=[dataset_filepath]))

    for f in dataset.files:
        assert f.status == "DOWNLOADED"

    datafile_ids = [f.id for f in dataset.files]

    dataset = client.call(
        ProcessCSV(dataset_id=dataset.id, datafile_ids=datafile_ids, wait=True)
    )


def test_create_dataset_v2_from_csv_fails(indico):
    client = IndicoClient()
    dataset = client.call(CreateDataset_v2(name=f"dataset-{int(time.time())}"))
    dataset_filepath = str(Path(__file__).parents[1]) + "/data/AirlineComplaints.csv"
    dataset = client.call(AddFiles(dataset_id=dataset.id, files=[dataset_filepath]))

    for f in dataset.files:
        assert f.status == "DOWNLOADED"

    datafile_ids = [f.id for f in dataset.files]

    dataset = client.call(
        ProcessFiles(dataset_id=dataset.id, datafile_ids=datafile_ids, wait=True)
    )
    # Need to use ProcessCSV
    assert dataset.files[0].status == "FAILED"


def test_create_dataset_v2_image_local_images(indico):
    client = IndicoClient()
    dataset_filepath = str(Path(__file__).parents[1]) + "/data/dog_vs_cats_small.csv"
    dataset = client.call(
        CreateDataset_v2(name=f"dataset-{int(time.time())}", dataset_type="IMAGE")
    )
    dataset = client.call(
        AddFiles(dataset_id=dataset.id, files=dataset_filepath, from_local_images=True)
    )

    for f in dataset.files:
        assert f.status == "DOWNLOADED"

    datafile_ids = [f.id for f in dataset.files]

    dataset = client.call(
        ProcessCSV(dataset_id=dataset.id, datafile_ids=datafile_ids, wait=True)
    )


def test_create_dataset_v2_image_links(indico):
    pass
