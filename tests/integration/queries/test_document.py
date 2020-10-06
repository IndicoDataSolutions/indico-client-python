import os
from pathlib import Path
from indico.client import IndicoClient
from indico.queries import (
    RetrieveStorageObject,
    JobStatus,
    DocumentExtraction,
    UploadBatched,
    UploadDocument,
)


def test_document_extraction(indico):
    client = IndicoClient()
    dataset_filepath = str(Path(__file__).parents[1]) + "/data/mock.pdf"

    jobs = client.call(DocumentExtraction(files=[dataset_filepath]))

    assert len(jobs) == 1
    job = jobs[0]
    assert job.id is not None
    job = client.call(JobStatus(id=job.id, wait=True))
    assert job.status == "SUCCESS"
    assert job.ready is True
    assert type(job.result["url"]) == str

    extract = client.call(RetrieveStorageObject(job.result))

    assert type(extract) == dict
    assert "pages" in extract


def test_document_extraction_with_config(indico):
    client = IndicoClient()
    dataset_filepath = str(Path(__file__).parents[1]) + "/data/mock.pdf"

    jobs = client.call(
        DocumentExtraction(
            files=[dataset_filepath], json_config={"preset_config": "simple"}
        )
    )

    assert len(jobs) == 1
    job = jobs[0]
    assert job.id is not None
    job = client.call(JobStatus(id=job.id, wait=True))
    assert job.status == "SUCCESS"
    assert job.ready is True
    assert type(job.result["url"]) == str

    extract = client.call(RetrieveStorageObject(job.result))

    assert type(extract) == dict
    assert "pages" in extract


def test_document_extraction_with_string_config(indico):
    client = IndicoClient()
    dataset_filepath = str(Path(__file__).parents[1]) + "/data/mock.pdf"

    jobs = client.call(
        DocumentExtraction(
            files=[dataset_filepath], json_config='{"preset_config": "simple"}'
        )
    )

    assert len(jobs) == 1
    job = jobs[0]
    assert job.id is not None
    job = client.call(JobStatus(id=job.id, wait=True))
    assert job.status == "SUCCESS"
    assert job.ready is True
    assert type(job.result["url"]) == str

    extract = client.call(RetrieveStorageObject(job.result))
    assert type(extract) == dict
    assert "pages" in extract


def test_upload_documents_batched(indico):
    file_names = ["mock.pdf", "mock_2.pdf", "mock_3.pdf"]
    client = IndicoClient()
    parent_path = str(Path(__file__).parent.parent / "data")
    dataset_filepaths = [
        os.path.join(parent_path, file_name) for file_name in file_names
    ]

    files = client.call(
        UploadBatched(files=dataset_filepaths, batch_size=1, request_cls=UploadDocument)
    )
    assert len(files) == 3
    for file_name, file in zip(file_names, files):
        assert file["filename"] == file_name


def test_document_extraction_batched(indico):
    client = IndicoClient()
    file_names = ["mock.pdf", "mock_2.pdf", "mock_3.pdf"]
    parent_path = str(Path(__file__).parent.parent / "data")
    dataset_filepaths = [
        os.path.join(parent_path, file_name) for file_name in file_names
    ]

    jobs = client.call(
        DocumentExtraction(
            files=dataset_filepaths,
            json_config={"preset_config": "simple"},
            upload_batch_size=1,
        )
    )
    assert len(jobs) == 3
    for job in jobs:
        assert job.id is not None
        job = client.call(JobStatus(id=job.id, wait=True))
        assert job.status == "SUCCESS"
        assert job.ready is True
        assert isinstance(job.result["url"], str)

def test_document_extraction_thumbnails(indico):
    client = IndicoClient()
    dataset_filepath = str(Path(__file__).parents[1]) + "/data/mock.pdf"

    jobs = client.call(DocumentExtraction(files=[dataset_filepath]))

    assert len(jobs) == 1
    job = jobs[0]
    assert job.id is not None
    job = client.call(JobStatus(id=job.id, wait=True))
    assert job.status == "SUCCESS"
    assert job.ready is True
    assert type(job.result["url"]) == str

    extract = client.call(RetrieveStorageObject(job.result))

    assert type(extract) == dict
    assert "pages" in extract
    image = extract["pages"][0]["image"]

    image = client.call(RetrieveStorageObject(image))

    assert image

def test_upload_duplicate_documents(indico):
    client = IndicoClient()
    file_names = ["mock.pdf", "mock.pdf", "mock_2.pdf"]
    parent_path = str(Path(__file__).parent.parent / "data")
    filepaths = [
        os.path.join(parent_path, file_name) for file_name in file_names
    ]
    uploaded_files = client.call(
        UploadDocument(files=filepaths)
    )
    assert len(uploaded_files) == 3
    assert [f["filename"] for f in uploaded_files] == file_names
