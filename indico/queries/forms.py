from typing import List
from pathlib import Path

from indico.client.request import RequestChain, GraphQLRequest
from indico.queries.storage import UploadBatched, UploadDocument
from indico.queries.jobs import Job

class _FormPreprocessing(GraphQLRequest):

    query = """
        mutation($files: [FileInput], $filenames: [String]) {
            activeFormFields(
                files: $files, filenames: $filenames
            ) {
                jobIds
            }
        }
    """

    def __init__(self, files, filenames):
        super().__init__(
            query=self.query, variables={"files": files, "filenames": filenames}
        )

    def process_response(self, response):
        jobs = super().process_response(response)["activeFormFields"]["jobIds"]
        if jobs:
            return [Job(id=j) for j in jobs]
        else:
            return []


# TODO: move into indico-client
class FormPreprocessing(RequestChain):

    def __init__(
        self, files: List[str], json_config: dict = None, upload_batch_size: int = None
    ):
        self.files = files
        self.upload_batch_size = upload_batch_size

    def requests(self):
        if self.upload_batch_size:
            yield UploadBatched(
                files=self.files,
                batch_size=self.upload_batch_size,
                request_cls=UploadDocument,
            )
        else:
            yield UploadDocument(files=self.files)
        yield _FormPreprocessing(files=self.previous, filenames=[Path(f).name for f in self.files])