import os
import time
import pytest
from pathlib import Path

from indico.client import IndicoClient
from indico.queries.datasets import (
    GetDatasetFileStatus,
    CreateDataset_v2,
    AddFiles,
    ProcessFiles,
    ProcessCSV,
)


def test_create_dataset_v2_from_files_document(indico):
    client = IndicoClient()

    dataset = client.call(CreateDataset_v2(name=f"dataset-{int(time.time())}"))

    file_names = ["us_doi.tiff"]
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


def test_create_dataset_v2_from_files_image(indico):
    client = IndicoClient()

    dataset = client.call(
        CreateDataset_v2(name=f"dataset-{int(time.time())}", dataset_type="IMAGE")
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

    dataset_filepath = str(Path(__file__).parents[1]) + "/data/AirlineComplaints.csv"
    dataset = client.call(AddFiles(dataset_id=dataset.id, files=[dataset_filepath]))
    datafile_ids = [f.id for f in dataset.files if f.status == "DOWNLOADED"]

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

    # Should raise invalid request
    dataset = client.call(
        ProcessFiles(dataset_id=dataset.id, datafile_ids=datafile_ids, wait=True)
    )


def test_create_dataset_v2_csv_image_links(indico):
    client = IndicoClient()
    dataset_filepath = str(Path(__file__).parents[1]) + "/data/image_link_small.csv"
    dataset = client.call(
        CreateDataset_v2(name=f"dataset-{int(time.time())}", dataset_type="IMAGE")
    )
    dataset = client.call(AddFiles(dataset_id=dataset.id, files=[dataset_filepath]))

    for f in dataset.files:
        assert f.status == "DOWNLOADED"

    datafile_ids = [f.id for f in dataset.files]

    dataset = client.call(
        ProcessCSV(dataset_id=dataset.id, datafile_ids=datafile_ids, wait=True)
    )


def test_create_dataset_v2_csv_image_links_with_broken(indico):
    client = IndicoClient()
    dataset_filepath = (
        str(Path(__file__).parents[1]) + "/data/image_link_small_with_broken.csv"
    )
    dataset = client.call(
        CreateDataset_v2(name=f"dataset-{int(time.time())}", dataset_type="IMAGE")
    )
    dataset = client.call(AddFiles(dataset_id=dataset.id, files=[dataset_filepath]))

    for f in dataset.files:
        assert f.status == "DOWNLOADED"

    datafile_ids = [f.id for f in dataset.files]

    dataset = client.call(
        ProcessCSV(dataset_id=dataset.id, datafile_ids=datafile_ids, wait=True)
    )


def test_create_dataset_v2_csv_pdf_links(indico):
    client = IndicoClient()
    dataset_filepath = str(Path(__file__).parents[1]) + "/data/pdf_links.csv"
    dataset = client.call(CreateDataset_v2(name=f"dataset-{int(time.time())}"))
    dataset = client.call(AddFiles(dataset_id=dataset.id, files=[dataset_filepath]))

    for f in dataset.files:
        assert f.status == "DOWNLOADED"

    datafile_ids = [f.id for f in dataset.files]

    dataset = client.call(
        ProcessCSV(dataset_id=dataset.id, datafile_ids=datafile_ids, wait=True)
    )


def test_csv_incompatible_columns(indico):
    client = IndicoClient()
    dataset_filepath = str(Path(__file__).parents[1]) + "/data/pdf_links.csv"
    dataset = client.call(CreateDataset_v2(name=f"dataset-{int(time.time())}"))
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
