from typing import TYPE_CHECKING, cast

from indico.client.request import GraphQLRequest, HTTPMethod, HTTPRequest, RequestChain
from indico.errors import IndicoInputError, IndicoRequestError
from indico.types.jobs import Job
from indico.types.model_export import ExportUpload

from .jobs import JobStatus
from .storage import storage_path

if TYPE_CHECKING:  # pragma: no cover
    from typing import Iterator, List, Optional, Union  # noqa: F401

    from indico.typing import AnyDict, Payload


class _GetExportUpload(GraphQLRequest["ExportUpload"]):
    query = """
        query exportUpload {
            exportUpload {
                uploadUrl
                storageUri
            }
        }
    """

    def __init__(self) -> None:
        super().__init__(self.query)

    def process_response(self, response: "Payload") -> ExportUpload:
        return ExportUpload(**super().parse_payload(response)["exportUpload"])


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
    ) -> "Iterator[Union[_GetExportUpload, HTTPRequest[List[AnyDict]], ProcessStaticModelExport, JobStatus]]":
        yield _GetExportUpload()
        upload: ExportUpload = self.previous

        yield HTTPRequest["List[AnyDict]"](
            HTTPMethod.POST,
            storage_path(upload.upload_url),
            files=[self.file_path],
            allow_redirects=False,
            timeout=None,
        )

        if not self.auto_process:
            self.result = upload.storage_uri
            return

        yield ProcessStaticModelExport(
            storage_uri=upload.storage_uri, workflow_id=cast(int, self.workflow_id)
        )
        yield JobStatus(self.previous.id)
        if self.previous.status == "FAILURE":
            raise IndicoRequestError(
                code="FAILURE",
                error=f"Failed to process static model export: {self.previous.result['message']}",
            )
