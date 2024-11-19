from typing import Generator

import requests

from indico.client.request import GraphQLRequest, RequestChain
from indico.errors import IndicoRequestError
from indico.queries.jobs import JobStatus
from indico.types.jobs import Job


class _UploadSMExport(GraphQLRequest):
    query = """
        query exportUpload {
            exportUpload {
                signedUrl
                storageUri
            }
        }
    """

    def __init__(self, file_path: str):
        self.file_path = file_path
        super().__init__(self.query)

    def process_response(self, response) -> str:
        resp = super().process_response(response)["exportUpload"]
        signed_url = resp["signedUrl"]
        storage_uri = resp["storageUri"]

        with open(self.file_path, "rb") as file:
            file_content = file.read()

        headers = {"Content-Type": "application/zip"}
        response = requests.put(signed_url, data=file_content, headers=headers)

        if response.status_code != 200:
            raise IndicoRequestError(
                f"Failed to upload static model export: {response.text}"
            )
        return storage_uri


class ProcessStaticModelExport(GraphQLRequest):
    """
    Process a static model export.

    Available on 6.14+ only.

    Args:
        storage_uri(str): the storage uri of the static model export that was uploaded to Indico.

    Returns:
        Job: the id of the job that is processing the static model export.
    """

    query = """
        mutation processStaticModelExport($storageUri: String!) {
            processStaticModelExport(storageUri: $storageUri) {
                jobId
            }
        }
    """

    def __init__(
        self,
        storage_uri: str | None = None,
    ):
        self.storage_uri = storage_uri
        super().__init__(
            self.query,
            variables={"storageUri": self.storage_uri},
        )

    def process_response(self, response) -> Job:
        job_id = super().process_response(response)["processStaticModelExport"]["jobId"]
        return Job(id=job_id)


class UploadStaticModelExport(RequestChain):
    """
    Upload a static model export to Indico.

    Available on 6.14+ only.

    Args:
        file_path(str): path to the export zip file to upload to Indico.

    Options:
        auto_process(bool): if True, the static model export will be processed after it is uploaded.

    Returns:
        str: the storage uri of the static model export.
    """

    def __init__(self, file_path: str, auto_process: bool = False):
        self.file_path = file_path
        self.auto_process = auto_process

    def requests(self) -> Generator[str | Job, None, None]:
        if self.auto_process:
            yield _UploadSMExport(self.file_path)
            yield ProcessStaticModelExport(self.previous)
            yield JobStatus(self.previous.id)
            if self.previous.status == "FAILURE":
                raise IndicoRequestError(
                    code="FAILURE",
                    error=f"Failed to process static model export: {self.previous.result['message']}",
                )
        else:
            yield _UploadSMExport(self.file_path)
