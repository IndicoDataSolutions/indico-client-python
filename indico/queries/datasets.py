# -*- coding: utf-8 -*-

import json
import tempfile
from pathlib import Path

from typing import List

from indico.client.request import GraphQLRequest, RequestChain, HTTPRequest, HTTPMethod
from indico.types.dataset import Dataset
from indico.errors import IndicoNotFound
from indico.queries.storage import UploadDocument


class ListDatasets(GraphQLRequest):
    """
    List all of your datasets

    Args:
        limit (int): Max number of datasets to retrieve. Default is 100

    Returns:
        List[Dataset]

    Raises:

    """

    query = """
        query ListDatasets($limit: Int){
            datasetsPage(limit: $limit) {
                datasets {
                    id
                    name
                    rowCount
                }
            }
        }
    """

    def __init__(self, limit: int = 100):
        super().__init__(self.query, variables={"limit": limit})

    def process_response(self, response) -> Dataset:
        response = super().process_response(response)
        return [Dataset(**dataset) for dataset in response["datasetsPage"]["datasets"]]


class GetDataset(GraphQLRequest):
    """
    Retrieve a dataset description object 

    Args:
        id (int): id of the dataset to query

    Returns:
        Dataset object

    Raises:

    """

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
        if not "dataset" in response or not isinstance(response["dataset"], dict):
            raise IndicoNotFound("Failed to find dataset")
        return Dataset(**response["dataset"])


class GetDatasetFileStatus(GetDataset):
    """
    Get the status of dataset file upload

    Args:
        id (int): id of the dataset to query
    
    Returns:
        status (str): DOWNLOADED or FAILED
    
    Raises:
        
    """

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
    """
    Get the status of a dataset 

    Args:
        id (int): id of the dataset to query

    Returns:
        status (str): COMPLETE or FAILED

    Raises:

    """

    query = """
        query datasetStatus($id: Int!) {
            dataset(id: $id) {
                status
            }
        }
    """

    def __init__(self, id: int):
        super().__init__(self.query, variables={"id": id})

    def process_response(self, response) -> str:
        return response["data"]["dataset"]["status"]


class CreateDataset(RequestChain):
    """
    Create a dataset and upload the associated files.

    Args:
        name (str): Name of the dataset
        files (List[str]): List of pathnames to the dataset files
        wait (bool): Wait for the dataset to upload and finish

    Returns:
        Dataset object

    Raises:

    """

    previous = None

    def __init__(
        self,
        name: str,
        files: List[str],
        wait: bool = True,
        from_local_images: bool = False,
    ):
        self.files = files
        self.name = name
        self.wait = wait
        self.from_local_images = from_local_images
        super().__init__()

    def requests(self):
        if self.from_local_images:
            yield UploadImages(self.files)
            with tempfile.TemporaryDirectory() as tmpdir:
                image_csv_path = str(Path(tmpdir) / "image_urls.csv")
                with open(str(image_csv_path), "w") as csv_file:
                    csv_file.write(self.previous)
                yield _UploadDatasetFiles(files=[image_csv_path])
        else:
            yield _UploadDatasetFiles(files=self.files)
        yield _CreateDataset(metadata=self.previous)
        dataset_id = self.previous.id
        yield GetDatasetFileStatus(id=dataset_id)
        while not all(
            f.status in ["DOWNLOADED", "FAILED"] for f in self.previous.files
        ):
            yield GetDatasetFileStatus(id=self.previous.id)
        yield _ProcessDataset(id=self.previous.id, name=self.name)
        yield GetDatasetStatus(id=dataset_id)
        if self.wait == True:
            while not self.previous in ["COMPLETE", "FAILED"]:
                yield GetDatasetStatus(id=dataset_id)
        yield GetDataset(id=dataset_id)


class _UploadDatasetFiles(HTTPRequest):
    def __init__(self, files: List[str]):
        super().__init__(
            method=HTTPMethod.POST, path="/storage/files/upload", files=files
        )


class UploadImages(UploadDocument):
    """
    Upload image files stored on a local filepath to the indico platform.
    """

    def process_response(self, uploaded_files: List[dict]) -> str:
        urls = [f["path"] for f in uploaded_files]
        files_string = "image_urls\n" + "\n".join(urls)
        return files_string


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
        return Dataset(**super().process_response(response)["processDataset"])
