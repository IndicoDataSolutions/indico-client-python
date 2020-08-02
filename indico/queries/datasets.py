# -*- coding: utf-8 -*-

import json
import tempfile
import pandas as pd
from pathlib import Path

from typing import List

from indico.client.request import (
    GraphQLRequest,
    RequestChain,
    HTTPRequest,
    HTTPMethod,
    Debouncer,
)
from indico.types.dataset import Dataset
from indico.errors import IndicoNotFound, IndicoInputError
from indico.queries.storage import URL_PREFIX, UploadBatched, UploadImages


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
        image_filename_col: str = "filename",
        batch_size: int = 20,
    ):
        self.files = files
        self.name = name
        self.wait = wait
        self.from_local_images = from_local_images
        self.image_filename_col = image_filename_col
        self.batch_size = batch_size
        super().__init__()

    def requests(self):
        if self.from_local_images:
            # Assume image filenames are in the same directory as the csv with
            # image labels and that there is a column representing their name
            df = pd.read_csv(self.files)
            img_filenames = df[self.image_filename_col].tolist()
            img_filepaths = [
                str(Path(self.files).parent / imgfn) for imgfn in img_filenames
            ]
            yield UploadBatched(
                img_filepaths, batch_size=self.batch_size, request_cls=UploadImages,
            )
            df["urls"] = self.previous
            with tempfile.TemporaryDirectory() as tmpdir:
                image_csv_path = str(Path(tmpdir) / "image_urls.csv")
                df.to_csv(image_csv_path)
                yield _UploadDatasetFiles(files=[image_csv_path])
        else:
            yield UploadBatched(
                files=self.files,
                batch_size=self.batch_size,
                request_cls=_UploadDatasetFiles,
            )
        yield _CreateDataset(metadata=self.previous)
        dataset_id = self.previous.id
        yield GetDatasetFileStatus(id=dataset_id)
        debouncer = Debouncer()
        while not all(
            f.status in ["DOWNLOADED", "FAILED"] for f in self.previous.files
        ):
            yield GetDatasetFileStatus(id=self.previous.id)
            debouncer.backoff()
        yield _ProcessDataset(id=self.previous.id, name=self.name)
        yield GetDatasetStatus(id=dataset_id)
        debouncer = Debouncer()
        if self.wait is True:
            while not self.previous in ["COMPLETE", "FAILED"]:
                yield GetDatasetStatus(id=dataset_id)
                debouncer.backoff()
        yield GetDataset(id=dataset_id)


class _UploadDatasetFiles(HTTPRequest):
    def __init__(self, files: List[str]):
        super().__init__(
            method=HTTPMethod.POST, path="/storage/files/upload", files=files
        )


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


class DeleteDataset(GraphQLRequest):
    """
    Delete a dataset

    Args:
        id (int): ID of the dataset

    Returns:
        success (bool): The success of the operation

    Raises:

    """

    query = """
    mutation deleteDataset($id: Int!) {
        deleteDataset(id: $id) {
            success
        }
    }
    """

    def __init__(self, id):
        super().__init__(self.query, variables={"id": id})

    def process_response(self, response):
        return super().process_response(response)["deleteDataset"]["success"]


class CreateDataset_v2(GraphQLRequest):
    query = """
    mutation($name: String!, $datasetType: DatasetType) {
        createDataset(name: $name, datasetType: $datasetType) {
            id
            name
        }
    }  
    """

    def __init__(self, name, dataset_type):
        if dataset_type not in ["TEXT", "IMAGE"]:
            raise IndicoInputError("Dataset Type must be TEXT or IMAGE")

        super().__init__(
            self.query, variables={"name": name, "datasetType": dataset_type}
        )

    def process_response(self, response):
        return Dataset(**super().process_response(response)["createDataset"])


#########################
## Dataset Pipeline v2 ##
#########################


class AddFiles(RequestChain):
    """
    TODO: WRITE DOCSTRING
    """

    previous = None

    def __init__(
        self,
        name: str,
        files: List[str],
        wait: bool = True,
        from_local_images: bool = False,
        image_filename_col: str = "filename",
        batch_size: int = 20,
    ):
        self.files = files
        self.name = name
        self.wait = wait
        self.from_local_images = from_local_images
        self.image_filename_col = image_filename_col
        self.batch_size = batch_size
        super().__init__()

    def requests(self):
        if self.from_local_images:
            # Assume image filenames are in the same directory as the csv with
            # image labels and that there is a column representing their name
            df = pd.read_csv(self.files)
            img_filenames = df[self.image_filename_col].tolist()
            img_filepaths = [
                str(Path(self.files).parent / imgfn) for imgfn in img_filenames
            ]
            yield UploadBatched(
                img_filepaths, batch_size=self.batch_size, request_cls=UploadImages,
            )
            df["urls"] = self.previous
            with tempfile.TemporaryDirectory() as tmpdir:
                image_csv_path = str(Path(tmpdir) / "image_urls.csv")
                df.to_csv(image_csv_path)
                yield _UploadDatasetFiles(files=[image_csv_path])
        else:
            yield UploadBatched(
                files=self.files,
                batch_size=self.batch_size,
                request_cls=_UploadDatasetFiles,
            )
        yield _CreateDataset(metadata=self.previous)
        dataset_id = self.previous.id
        yield GetDatasetFileStatus(id=dataset_id)
        debouncer = Debouncer()
        while not all(
            f.status in ["DOWNLOADED", "FAILED"] for f in self.previous.files
        ):
            yield GetDatasetFileStatus(id=self.previous.id)
            debouncer.backoff()


class _ProcessFiles(GraphQLRequest):
    query = """
    mutation (
        $datasetId: Int!, 
        $datafileIds: [Int], 
        $datacolumnId: Int, 
        $datacolumnName: String) {
        addDataFiles(
          datasetId: $datasetId, 
          datafileIds: $datafileIds, 
          datacolumnId: $datacolumnId, 
          datacolumnName: $datacolumnName) {
            id
            name
        }
    }
    """

    def __init__(self, dataset_id, datafile_ids, datacolumn_id, datacolumn_name):
        super().__init__(
            self.query,
            variables={
                "datasetId": dataset_id,
                "datafileIds": datafile_ids,
                "datacolumnId": datacolumn_id,
                "datacolumnName": datacolumn_name,
            },
        )

    def process_response(self, response):
        return Dataset(**super().process_response(response)["addDataFiles"])


class _ProcessCSV(GraphQLRequest):
    query = """
    mutation ($datasetId: Int!, $datafileIds: [Int]) {
        addDataCsv(datasetId: $datasetId, datafileIds: $datafileIds) {
            id
            name
        }
    }
    """

    def __init__(self, dataset_id, datafile_ids):
        super().__init__(
            self.query, variables={"datasetId": dataset_id, "datafileIds": datafile_ids}
        )

    def process_response(self, response):
        return Dataset(**super().process_response(response)["addDataCsv"])


class ProcessFiles(RequestChain):
    """
    TODO: DOCSTRING
    """

    def __init__(
        self, dataset_id, datafile_ids, datacolumn_id, datacolumn_name, wait=True
    ):
        self.dataset_id = dataset_id
        self.datafile_ids = datafile_ids
        self.datacolumn_id = datacolumn_id
        self.datacolumn_name = datacolumn_name
        self.wait = wait

    def requests(self):
        yield _ProcessFiles(
            self.dataset_id, self.datafile_ids, self.datacolumn_id, self.datacolumn_name
        )
        debouncer = Debouncer()
        yield GetDatasetFileStatus(id=self.dataset_id)
        while not all(
            f.status in ["DOWNLOADED", "FAILED"] for f in self.previous.files
        ):
            yield GetDatasetFileStatus(id=self.dataset_id)
            debouncer.backoff()


class ProcessCSV(RequestChain):
    """
    TODO: DOCSTRING
    """

    def __init__(self, dataset_id, datafile_ids):
        self.dataset_id = dataset_id
        self.datafile_ids = datafile_ids

    def requests(self):
        yield _ProcessCSV(self.dataset_id, self.datafile_ids)
        debouncer = Debouncer()
        yield GetDatasetFileStatus(id=self.dataset_id)
        while not all(
            f.status in ["DOWNLOADED", "FAILED"] for f in self.previous.files
        ):
            yield GetDatasetFileStatus(id=self.dataset_id)
            debouncer.backoff()

