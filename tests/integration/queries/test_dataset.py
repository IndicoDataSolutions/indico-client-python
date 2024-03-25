import json
import os
import time
from pathlib import Path

import pandas as pd
import pytest

from indico.client import IndicoClient
from indico.errors import IndicoRequestError
from indico.filters import DatasetFilter
from indico.queries.datasets import (
    AddFiles,
    CreateDataset,
    CreateEmptyDataset,
    DeleteDataset,
    GetDataset,
    GetDatasetFileStatus,
    ListDatasets,
)
from indico.queries.export import CreateExport, DownloadExport
from indico.types.dataset import (
    Dataset,
    OcrEngine,
    OmnipageOcrOptionsInput,
    ReadApiOcrOptionsInput,
    TableReadOrder,
)
from tests.integration.data.datasets import airlines_dataset  # noqa: F401


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


def test_list_datasets_filtered(indico, airlines_dataset):
    client = IndicoClient()
    datasets = client.call(
        ListDatasets(filters=DatasetFilter(name=f"{time.time()}_bananas"))
    )

    assert isinstance(datasets, list)
    assert len(datasets) == 0

    # happy path
    datasets = client.call(
        ListDatasets(filters=DatasetFilter(name=airlines_dataset.name))
    )

    assert isinstance(datasets, list)
    assert len(datasets) == 1
    assert type(datasets[0]) == Dataset
    assert datasets[0].name == airlines_dataset.name


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


@pytest.mark.ocr("omnipage")
def test_create_with_options(indico):
    client = IndicoClient()
    config: OmnipageOcrOptionsInput = {
        "auto_rotate": True,
        "single_column": True,
        "upscale_images": True,
        "languages": ["ENG", "FIN"],
        "force_render": False,
        "native_layout": False,
        "native_pdf": False,
        "table_read_order": TableReadOrder.ROW,
    }
    dataset = client.call(
        CreateEmptyDataset(
            name=f"dataset-{int(time.time())}",
            ocr_engine=OcrEngine.OMNIPAGE,
            omnipage_ocr_options=config,
        )
    )


@pytest.mark.ocr("readapi")
def test_create_with_options_readapi(indico):
    client = IndicoClient()
    config: ReadApiOcrOptionsInput = {
        "auto_rotate": True,
        "single_column": False,
        "upscale_images": True,
        "languages": ["AUTO"],
    }
    dataset = client.call(
        CreateEmptyDataset(
            name=f"dataset-{int(time.time())}",
            ocr_engine=OcrEngine.READAPI,
            readapi_ocr_options=config,
        )
    )


@pytest.mark.ocr("readapi_v2")
def test_create_from_files_with_readapiv2(indico):
    client = IndicoClient()
    dataset = client.call(
        CreateEmptyDataset(
            name=f"dataset-{int(time.time())}", ocr_engine=OcrEngine.READAPI_V2
        )
    )
    file_names = ["us_doi.tiff", "mock.pdf"]
    parent_path = str(Path(__file__).parent.parent / "data")
    dataset_filepaths = [
        os.path.join(parent_path, file_name) for file_name in file_names
    ]

    dataset = client.call(
        AddFiles(dataset_id=dataset.id, files=[dataset_filepaths[0]], autoprocess=True)
    )
    dataset = client.call(
        AddFiles(dataset_id=dataset.id, files=[dataset_filepaths[1]], autoprocess=True)
    )

    _dataset_complete(dataset)


def test_create_from_files_document(indico):
    client = IndicoClient()
    dataset = client.call(CreateEmptyDataset(name=f"dataset-{int(time.time())}"))
    file_names = ["us_doi.tiff", "mock.pdf"]
    parent_path = str(Path(__file__).parent.parent / "data")
    dataset_filepaths = [
        os.path.join(parent_path, file_name) for file_name in file_names
    ]

    dataset = client.call(
        AddFiles(dataset_id=dataset.id, files=[dataset_filepaths[0]], autoprocess=True)
    )
    dataset = client.call(
        AddFiles(dataset_id=dataset.id, files=[dataset_filepaths[1]], autoprocess=True)
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

    dataset = client.call(
        AddFiles(dataset_id=dataset.id, files=dataset_filepaths, autoprocess=True)
    )

    file_names = ["4.jpg", "5.jpg"]
    dataset_filepaths = [
        os.path.join(parent_path, file_name) for file_name in file_names
    ]

    dataset = client.call(
        AddFiles(dataset_id=dataset.id, files=dataset_filepaths, autoprocess=True)
    )
    _dataset_complete(dataset)


def test_create_from_csv(indico):
    client = IndicoClient()
    dataset = client.call(CreateEmptyDataset(name=f"dataset-{int(time.time())}"))
    dataset_filepath = str(Path(__file__).parents[1]) + "/data/AirlineComplaints.csv"
    dataset = client.call(
        AddFiles(dataset_id=dataset.id, files=[dataset_filepath], autoprocess=True)
    )
    _dataset_complete(dataset)
    full_dataset = dataset = client.call(GetDataset(id=dataset.id))
    export = client.call(
        CreateExport(
            dataset_id=full_dataset.id,
            labelset_id=full_dataset.labelsets[0].id,
            wait=True,
        )
    )

    exported_data = client.call(DownloadExport(export.id))
    exported_data.to_csv("test.csv")
    baseline_data = pd.read_csv(dataset_filepath)
    for col in baseline_data.columns:
        assert col in exported_data.columns
    assert (baseline_data["Text"] == exported_data["Text"]).all()
    export_labels = exported_data["Target_1"].apply(
        lambda x: json.loads(x)["targets"][0]["label"]
    )
    assert (baseline_data["Target_1"].str.strip() == export_labels).all()


def test_create_from_csv_image_urls(indico):
    client = IndicoClient()
    dataset_filepath = str(Path(__file__).parents[1]) + "/data/image_link_small.csv"
    dataset = client.call(
        CreateEmptyDataset(name=f"dataset-{int(time.time())}", dataset_type="IMAGE")
    )
    dataset = client.call(
        AddFiles(dataset_id=dataset.id, files=[dataset_filepath], autoprocess=True)
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
    dataset = client.call(
        AddFiles(dataset_id=dataset.id, files=[dataset_filepath], autoprocess=True)
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
    dataset = client.call(
        AddFiles(dataset_id=dataset.id, files=[dataset_filepath], autoprocess=True)
    )

    _dataset_complete(dataset)


def test_csv_incompat_columns(indico):
    client = IndicoClient()
    dataset_filepath = str(Path(__file__).parents[1]) + "/data/pdf_links.csv"
    dataset = client.call(CreateEmptyDataset(name=f"dataset-{int(time.time())}"))
    dataset = client.call(
        AddFiles(dataset_id=dataset.id, files=[dataset_filepath], autoprocess=True)
    )

    for f in dataset.files:
        assert f.status == "PROCESSED"

    dataset_filepath = str(Path(__file__).parents[1]) + "/data/AirlineComplaints.csv"
    dataset = client.call(
        AddFiles(dataset_id=dataset.id, files=[dataset_filepath], autoprocess=True)
    )

    failed = 0
    for df in dataset.files:
        if df.status == "FAILED":
            assert df.failure_type == "INCOMPATIBLE_CSV_COLUMNS"
            failed += 1
        else:
            assert df.status == "PROCESSED"

    assert dataset.status == "COMPLETE"


def test_bad_csv_create_dataset(indico):
    client = IndicoClient()
    dataset_filepath = str(Path(__file__).parents[1]) + "/data/classification.csv"
    dataset = client.call(
        CreateDataset(
            name=f"dataset-{int(time.time())}", files=[dataset_filepath], wait=True
        ),
    )

    assert dataset.status == "CREATING"
    dataset = client.call(GetDatasetFileStatus(id=dataset.id))
    assert all([f.status == "FAILED" for f in dataset.files])
