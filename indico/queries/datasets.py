import json
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
                datacolumns {
                    id
                    name
                }
                labelsets{
                    id
                    name
                }
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
    def  __init__(self, id: int):
        super().__init__(self.query, variables={
            "id": id
        })

    def process_response(self, response) -> str:
        return response["data"]["dataset"]["status"]


class CreateDataset(RequestChain):
    previous = None
    def __init__(self, name: str, files: List[str], wait=True):
        self.files = files
        self.name = name
        self.wait = wait
        super().__init__()

    def requests(self):
        yield _UploadDatasetFiles(files=self.files)
        yield _CreateDataset(metadata=self.previous)
        dataset_id = self.previous.id
        yield GetDatasetFileStatus(id=dataset_id)
        while not all(f.status in ["DOWNLOADED", "FAILED"] for f in self.previous.files):
            yield GetDatasetFileStatus(id=self.previous.id)
        yield _ProcessDataset(id=self.previous.id, name=self.name)
        yield GetDatasetStatus(id=dataset_id)
        if self.wait == True:
            while not self.previous in ["COMPLETE", "FAILED"]:
                yield GetDatasetStatus(id=dataset_id)
        yield GetDataset(id=dataset_id)


class _UploadDatasetFiles(HTTPRequest):
    def __init__(self, files: List[str]):
        super().__init__(method=HTTPMethod.POST, path="/storage/files/upload", files=files)

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
        print(metadata)
        super().__init__(self.query, variables={"metadata": json.dumps(metadata)})

    def process_response(self, response):
        return Dataset(**super().process_response(response)["newDataset"])

    
class _ProcessDataset(GraphQLRequest):
    query = """
        mutation ProcessDataset($id: Int!, $name: String) {
            processDataset(datasetId: $id, name: $name) {
                    id
                    status
            }
        }
    """

    def __init__(self, id, name):
        super().__init__(self.query, variables={"id": id, "name": name})

    def process_response(self, response):
        print(response)
        return Dataset(**super().process_response(response)["processDataset"])

