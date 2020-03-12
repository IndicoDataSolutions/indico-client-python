from typing import List

from indico.client.request import GraphQLRequest, RequestChain, HTTPRequest, HTTPMethod
from indico.types.dataset import Dataset


class GetDataset(GraphQLRequest):
    query = """
        query GetDataset($id: Int) {
	        dataset(id: $id) {
                id
                name    
                rowCount
                status
                permissions
            }
        }
    """

    def __init__(self, id: int):
        super().__init__(self.query, variables={"id": id})
    
    def process_response(self, response) -> Dataset:
        response = super().process_response(response)
        print
        return Dataset(**response["dataset"])


class GetDatasetFileStatus(GetDataset):
    query = """
        query DatasetUploadStatus($id: Int!) {
            dataset(id: $id) {
                id
                status
                files {
                    id
                    name
                    deleted
                    fileSize
                    rainbowUrl
                    fileType
                    fileHash
                    status
                    statusMeta
                }
            }
        }
    """


class GetDatasetStatus(GraphQLRequest):
    query = """
        query datasetStatus($id: Int!) {
            dataset(id: $id) {
                status
            }
        }
    """

    def process_response(self, response) -> str:
        return response["data"]["dataset"]["status"]


class CreateDataset(RequestChain):

    def __init__(self, name: str, files: List[str]):
        self.files = files
        self.name = name
        super().__init__()

    def _upload_files(self):
        _UploadDatasetFiles(files=self.files)

    def check_file_status(self):
        return lambda dataset: GetDatasetFileStatus(id=dataset.id)

    def _create_dataset(self):
        return lambda metadata: _CreateDataset(metadata)

    def _process_dataset(self):
        return lambda dataset: _ProcessDataset(dataset.id, self.name)

    def requests(self, previous):
        yield _UploadDatasetFiles(files=self.files)
        yield _CreateDataset(previous)
        while not previous.files or not all(previous.files in ["downloaded", "failed"]):
            yield GetDatasetFileStatus(id=previous.id)
        yield _ProcessDataset(id=previous.id, name=self.name)


class _UploadDatasetFiles(HTTPRequest):
    def __init__(self, files: List[str]):
        super().__init__(method=HTTPMethod.POST, path="")

class _CreateDataset(GraphQLRequest):
    query = """
        mutation CreateDataset($metadata: JSONString!) {
            newDataset(metadataList: $metadata) {
                id    
                status
            }
        }
    """

    def __init__(self, metadata: str):
        super().__init__(self.query, variables={"metadata": metadata})

    def process_response(self, response):
        return Dataset(**super().process_response(response))

    
class _ProcessDataset(GraphQLRequest):
    query = """
        mutation ProcessDataset($datasetId: Int!, $name: String) {
            processDataset(datasetId: $datasetId, name: $name) {
                    id
                    status
            }
        }
    """

    def __init__(self, id, name):
        super().__init__(self.query, variables={"id": id, "name": name})

    def process_response(self, response):
        return Dataset(**super().process_response(response))

