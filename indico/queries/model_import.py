from typing import TYPE_CHECKING, cast

import requests  # type: ignore

from indico.client.request import GraphQLRequest, RequestChain
from indico.errors import IndicoInputError, IndicoRequestError
from indico.types.jobs import Job

from .jobs import JobStatus

if TYPE_CHECKING:  # pragma: no cover
    from typing import Dict, Iterator, Optional, Union  # noqa: F401

    from indico.typing import Payload


class _UploadSMExport(GraphQLRequest[str]):
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

    def process_response(self, response: "Payload") -> str:
        resp: "Dict[str, str]" = super().parse_payload(response)["exportUpload"]
        signed_url = resp["signedUrl"]
        storage_uri = resp["storageUri"]

        with open(self.file_path, "rb") as file:
            file_content = file.read()

        headers = {"Content-Type": "application/zip"}
        export_response = requests.put(signed_url, data=file_content, headers=headers)

        if export_response.status_code != 200:
            raise IndicoRequestError(
                f"Failed to upload static model export: {export_response.text}",
                export_response.status_code,
            )
        return storage_uri


class ProcessStaticModelExport(GraphQLRequest["Job"]):
    """
    Process a static model export.

    Available on 6.14+ only.

    Args:
        storage_uri(str): the storage uri of the static model export that was uploaded to Indico.
        workflow_id(int): the id of the workflow that the static model export is being added to.

    Returns:
        Job: the id of the job that is processing the static model export.
    """

    query = """
        mutation processStaticModelExport($storageUri: String!, $workflowId: Int!) {
            processStaticModelExport(storageUri: $storageUri, workflowId: $workflowId) {
                jobId
            }
        }
    """

    def __init__(
        self,
        storage_uri: str,
        workflow_id: int,
    ):
        self.storage_uri = storage_uri
        self.workflow_id = workflow_id
        super().__init__(
            self.query,
            variables={
                "storageUri": self.storage_uri,
                "workflowId": self.workflow_id,
            },
        )

    def process_response(self, response: "Payload") -> Job:
        job_id = super().parse_payload(response)["processStaticModelExport"]["jobId"]
        return Job(id=job_id)


class UploadStaticModelExport(RequestChain["Union[Job, str]"]):
    """
    Upload a static model export to Indico.

    Available on 6.14+ only.

    Args:
        file_path(str): path to the export zip file to upload to Indico.

    Options:
        auto_process(bool): if True, the static model export will be processed after it is uploaded.
        workflow_id(int): the id of the workflow that the static model export is being added to. Required if `auto_process` is True.

    Returns:
        str: the storage uri of the static model export.
    """

    def __init__(
        self,
        file_path: str,
        auto_process: bool = False,
        workflow_id: "Optional[int]" = None,
    ):
        if auto_process and workflow_id is None:
            raise IndicoInputError(
                "Must provide `workflow_id` if `auto_process` is True."
            )

        self.file_path = file_path
        self.auto_process = auto_process
        self.workflow_id = workflow_id

    def requests(
        self,
    ) -> "Iterator[Union[_UploadSMExport, ProcessStaticModelExport, JobStatus]]":
        if self.auto_process:
            yield _UploadSMExport(self.file_path)
            yield ProcessStaticModelExport(
                storage_uri=self.previous, workflow_id=cast(int, self.workflow_id)
            )
            yield JobStatus(self.previous.id)
            if self.previous.status == "FAILURE":
                raise IndicoRequestError(
                    code="FAILURE",
                    error=f"Failed to process static model export: {self.previous.result['message']}",
                )
        else:
            yield _UploadSMExport(self.file_path)
