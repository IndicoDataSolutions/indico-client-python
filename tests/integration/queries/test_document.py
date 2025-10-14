import os
from pathlib import Path

from indico.client import IndicoClient
from indico.queries import UploadBatched, UploadDocument


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


def test_upload_duplicate_documents(indico):
    client = IndicoClient()
    file_names = ["mock.pdf", "mock.pdf", "mock_2.pdf"]
    parent_path = str(Path(__file__).parent.parent / "data")
    filepaths = [os.path.join(parent_path, file_name) for file_name in file_names]
    uploaded_files = client.call(UploadDocument(files=filepaths))
    assert len(uploaded_files) == 3
    assert [f["filename"] for f in uploaded_files] == file_names
