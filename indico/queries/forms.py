from typing import TYPE_CHECKING

from indico.client.request import GraphQLRequest, RequestChain
from indico.queries.storage import UploadBatched, UploadDocument
from indico.types import Job

if TYPE_CHECKING:  # pragma: no cover
    from typing import Iterator, List, Optional, Union

    from indico.typing import AnyDict, Payload


class _FormPreprocessing(GraphQLRequest["List[Job]"]):
    query = """
        mutation($files: [FileInput]) {
            activeFormFields(
                files: $files
            ) {
                jobIds
            }
        }
    """

    def __init__(self, files: "List[AnyDict]"):
        super().__init__(query=self.query, variables={"files": files})

    def process_response(self, response: "Payload") -> "List[Job]":
        jobs = super().parse_payload(response)["activeFormFields"]["jobIds"] or set()
        return [Job(id=j) for j in jobs]


# TODO: move into indico-client
class FormPreprocessing(RequestChain["List[Job]"]):
    """
    Attempt to auto-detect form fields and labels

    Args:
        files (str): list of filepaths to upload

    Returns:
        suggested_fields: list of dictionarys (1 per PDF) containing structured field data
    """

    def __init__(
        self,
        files: "List[str]",
        json_config: "Optional[AnyDict]" = None,
        upload_batch_size: "Optional[int]" = None,
    ):
        self.files = files
        self.upload_batch_size = upload_batch_size

    def requests(
        self,
    ) -> "Iterator[Union[UploadBatched, UploadDocument, _FormPreprocessing]]":
        if self.upload_batch_size:
            yield UploadBatched(
                files=self.files,
                batch_size=self.upload_batch_size,
                request_cls=UploadDocument,
            )
        else:
            yield UploadDocument(files=self.files)

        yield _FormPreprocessing(files=self.previous)
