import time
import pytest
import unittest
import pandas as pd
from pathlib import Path
import os
from indico.client import IndicoClient
from indico.queries.datasets import (
    GetDataset,
    GetDatasetFileStatus,
    CreateDataset,
    ListDatasets,
    DeleteDataset,
    CreateEmptyDataset,
    AddFiles,
    ProcessFiles,
    ProcessCSV,
)
from indico.queries.export import CreateExport, DownloadExport
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
        assert datafile.file_type == "PDF"


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


def _dataset_complete(dataset):
    for df in dataset.files:
        assert df.status == "PROCESSED"

    assert dataset.status == "COMPLETE"


def test_create_from_files_document(indico):
    client = IndicoClient()
    dataset = client.call(CreateEmptyDataset(name=f"dataset-{int(time.time())}"))
    file_names = ["us_doi.tiff", "mock.pdf"]
    parent_path = str(Path(__file__).parent.parent / "data")
    dataset_filepaths = [
        os.path.join(parent_path, file_name) for file_name in file_names
    ]

    dataset = client.call(AddFiles(dataset_id=dataset.id, files=[dataset_filepaths[0]]))

    for f in dataset.files:
        assert f.status == "DOWNLOADED"

    datafile_ids = [f.id for f in dataset.files]

    dataset = client.call(
        ProcessFiles(dataset_id=dataset.id, datafile_ids=datafile_ids, wait=True)
    )

    dataset = client.call(AddFiles(dataset_id=dataset.id, files=[dataset_filepaths[1]]))

    datafile_ids = [f.id for f in dataset.files if f.status == "DOWNLOADED"]

    dataset = client.call(
        ProcessFiles(dataset_id=dataset.id, datafile_ids=datafile_ids, wait=True)
    )

    _dataset_complete(dataset)


def test_create_from_files_image(indico):
    client = IndicoClient()
    dataset = client.call(
        CreateEmptyDataset(name=f"dataset-{int(time.time())}", dataset_type="IMAGE")
    )
    file_names = ["1.jpg", "2.jpg", "3.jpg"]
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

    file_names = ["4.jpg", "5.jpg"]
    dataset_filepaths = [
        os.path.join(parent_path, file_name) for file_name in file_names
    ]

    dataset = client.call(AddFiles(dataset_id=dataset.id, files=dataset_filepaths))

    datafile_ids = [f.id for f in dataset.files if f.status == "DOWNLOADED"]

    dataset = client.call(
        ProcessFiles(dataset_id=dataset.id, datafile_ids=datafile_ids, wait=True)
    )

    _dataset_complete(dataset)


def test_create_from_csv(indico):
    client = IndicoClient()
    dataset = client.call(CreateEmptyDataset(name=f"dataset-{int(time.time())}"))
    dataset_filepath = str(Path(__file__).parents[1]) + "/data/AirlineComplaints.csv"
    dataset = client.call(AddFiles(dataset_id=dataset.id, files=[dataset_filepath]))

    for f in dataset.files:
        assert f.status == "DOWNLOADED"

    datafile_ids = [f.id for f in dataset.files]

    dataset = client.call(
        ProcessCSV(dataset_id=dataset.id, datafile_ids=datafile_ids, wait=True)
    )

    dataset_filepath = str(Path(__file__).parents[1]) + "/data/AirlineComplaints.csv"
    dataset = client.call(AddFiles(dataset_id=dataset.id, files=[dataset_filepath]))
    datafile_ids = [f.id for f in dataset.files if f.status == "DOWNLOADED"]

    dataset = client.call(
        ProcessCSV(dataset_id=dataset.id, datafile_ids=datafile_ids, wait=True)
    )

    _dataset_complete(dataset)

    export = client.call(CreateExport(dataset_id=dataset.id, wait=True))

    exported_data = client.call(DownloadExport(export.id))

    baseline_data = pd.read_csv(dataset_filepath)

    for col in baseline_data.columns:
        assert all(
            baseline_data[col].apply(str).str.strip().values
            == exported_data[: len(baseline_data)][col].apply(str).values
        )
        assert all(
            baseline_data[col].apply(str).str.strip().values
            == exported_data[len(baseline_data) :][col].apply(str).values
        )


def test_create_from_csv_image_urls(indico):
    client = IndicoClient()
    dataset_filepath = str(Path(__file__).parents[1]) + "/data/image_link_small.csv"
    dataset = client.call(
        CreateEmptyDataset(name=f"dataset-{int(time.time())}", dataset_type="IMAGE")
    )
    dataset = client.call(AddFiles(dataset_id=dataset.id, files=[dataset_filepath]))

    for f in dataset.files:
        assert f.status == "DOWNLOADED"

    datafile_ids = [f.id for f in dataset.files]

    dataset = client.call(
        ProcessCSV(dataset_id=dataset.id, datafile_ids=datafile_ids, wait=True)
    )

    _dataset_complete(dataset)


def test_create_from_csv_image_urls_with_broken(indico):
    client = IndicoClient()
    dataset_filepath = (
        str(Path(__file__).parents[1]) + "/data/image_link_small_with_broken.csv"
    )
    dataset = client.call(
        CreateEmptyDataset(name=f"dataset-{int(time.time())}", dataset_type="IMAGE")
    )
    dataset = client.call(AddFiles(dataset_id=dataset.id, files=[dataset_filepath]))

    for f in dataset.files:
        assert f.status == "DOWNLOADED"

    datafile_ids = [f.id for f in dataset.files]

    dataset = client.call(
        ProcessCSV(dataset_id=dataset.id, datafile_ids=datafile_ids, wait=True)
    )

    failed = 0
    for df in dataset.files:
        if df.status == "FAILED":
            assert df.failure_type == "DOWNLOAD"
            failed += 1
        else:
            assert df.status == "PROCESSED"
    assert failed == 1


def test_create_from_csv_doc_urls(indico):
    client = IndicoClient()
    dataset_filepath = str(Path(__file__).parents[1]) + "/data/pdf_links.csv"
    dataset = client.call(CreateEmptyDataset(name=f"dataset-{int(time.time())}"))
    dataset = client.call(AddFiles(dataset_id=dataset.id, files=[dataset_filepath]))

    for f in dataset.files:
        assert f.status == "DOWNLOADED"

    datafile_ids = [f.id for f in dataset.files]

    dataset = client.call(
        ProcessCSV(dataset_id=dataset.id, datafile_ids=datafile_ids, wait=True)
    )

    _dataset_complete(dataset)


@unittest.skip
def test_csv_incompat_columns(indico):
    client = IndicoClient()
    dataset_filepath = str(Path(__file__).parents[1]) + "/data/pdf_links.csv"
    dataset = client.call(CreateEmptyDataset(name=f"dataset-{int(time.time())}"))
    dataset = client.call(AddFiles(dataset_id=dataset.id, files=[dataset_filepath]))

    for f in dataset.files:
        assert f.status == "DOWNLOADED"

    datafile_ids = [f.id for f in dataset.files]

    dataset = client.call(
        ProcessCSV(dataset_id=dataset.id, datafile_ids=datafile_ids, wait=True)
    )

    dataset_filepath = str(Path(__file__).parents[1]) + "/data/AirlineComplaints.csv"
    dataset = client.call(AddFiles(dataset_id=dataset.id, files=[dataset_filepath]))

    datafile_ids = [
        df.id
        for df in dataset.files
        if df.status == "DOWNLOADED" and df.file_type == "csv"
    ]

    dataset = client.call(
        ProcessCSV(dataset_id=dataset.id, datafile_ids=datafile_ids, wait=True)
    )

    failed = 0
    for df in dataset.files:
        if df.status == "FAILED":
            assert df.failure_type == "INCOMPATIBLE_CSV_COLUMNS"
            failed += 1
        else:
            assert df.status == "PROCESSED"

    assert dataset.status == "COMPLETE"

