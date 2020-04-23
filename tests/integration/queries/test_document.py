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
from indico.types.jobs import Job


def test_document_extraction(indico):
    client = IndicoClient()
    dataset_filepath = str(Path(__file__).parents[1]) + "/data/mock.pdf"

    jobs = client.call(DocumentExtraction(files=[dataset_filepath]))

    assert len(jobs) == 1
    job = jobs[0]
    assert job.id != None
    job = client.call(JobStatus(id=job.id, wait=True))
    assert job.status == "SUCCESS"
    assert job.ready == True
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
    assert job.id != None
    job = client.call(JobStatus(id=job.id, wait=True))
    assert job.status == "SUCCESS"
    assert job.ready == True
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
    assert job.id != None
    job = client.call(JobStatus(id=job.id, wait=True))
    assert job.status == "SUCCESS"
    assert job.ready == True
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
