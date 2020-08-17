import os
import time
import pandas as pd
import pytest
from pathlib import Path

from indico.client import IndicoClient
from indico.queries.datasets import (
    GetDatasetFileStatus,
    CreateEmptyDataset,
    AddFiles,
    ProcessFiles,
    ProcessCSV,
)
from indico.queries.export import CreateExport, DownloadExport


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

