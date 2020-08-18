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
                    failureType
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
        dataset_type (str): Type of dataset to create [TEXT, DOCUMENT, IMAGE]
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
        dataset_type: str = "TEXT",
        from_local_images: bool = False,
        image_filename_col: str = "filename",
        batch_size: int = 20,
    ):
        self.files = files
        self.name = name
        self.wait = wait
        self.dataset_type = dataset_type
        self.from_local_images = from_local_images
        self.image_filename_col = image_filename_col
        self.batch_size = batch_size
        super().__init__()

    def requests(self):
        if self.from_local_images:
            self.dataset_type = "IMAGE"
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
        file_metadata = self.previous
        yield CreateEmptyDataset(name=self.name, dataset_type=self.dataset_type)
        yield _AddFiles(dataset_id=self.previous.id, metadata=file_metadata)
        dataset_id = self.previous.id
        yield GetDatasetFileStatus(id=dataset_id)
        debouncer = Debouncer()
        while not all(
            f.status in ["DOWNLOADED", "FAILED"] for f in self.previous.files
        ):
            yield GetDatasetFileStatus(id=self.previous.id)
            debouncer.backoff()
        csv_files = [f.id for f in self.previous.files if f.file_type == "CSV"]
        non_csv_files = [f.id for f in self.previous.files if f.file_type != "CSV"]

        if csv_files:
            yield _ProcessCSV(dataset_id=dataset_id, datafile_ids=csv_files)
        elif non_csv_files:
            yield _ProcessFiles(dataset_id=dataset_id, datafile_ids=non_csv_files)
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


class CreateEmptyDataset(GraphQLRequest):
    query = """
    mutation($name: String!, $datasetType: DatasetType) {
        createDataset(name: $name, datasetType: $datasetType) {
            id
            name
        }
    }  
    """

    def __init__(self, name: str, dataset_type: str = None):
        if not dataset_type:
            dataset_type = "TEXT"

        super().__init__(
            self.query, variables={"name": name, "datasetType": dataset_type}
        )

    def process_response(self, response):
        return Dataset(**super().process_response(response)["createDataset"])


class _AddFiles(GraphQLRequest):
    query = """
    mutation AddFiles($datasetId: Int!, $metadata: JSONString!){
        addDatasetFiles(datasetId: $datasetId, metadataList: $metadata) {
            id
            status
        }
    }
    """

    def __init__(self, dataset_id: int, metadata: List[str]):
        super().__init__(
            self.query,
            variables={"datasetId": dataset_id, "metadata": json.dumps(metadata)},
        )

    def process_response(self, response):
        return Dataset(**super().process_response(response)["addDatasetFiles"])


class AddFiles(RequestChain):
    """
    Add files to a dataset

    Args:
        dataset_id (int): ID of the dataset
        files (List[str]): List of pathnames to the dataset files
        wait (bool): Block while polling for status of files
        batch_size (int): Batch size for uploading files

    Returns:
        Dataset

    Raises: 

    """

    previous = None

    def __init__(
        self,
        dataset_id: int,
        files: List[str],
        wait: bool = True,
        batch_size: int = 20,
    ):
        self.dataset_id = dataset_id
        self.files = files
        self.wait = wait
        self.batch_size = batch_size
        super().__init__()

    def requests(self):
        yield UploadBatched(
            files=self.files,
            batch_size=self.batch_size,
            request_cls=_UploadDatasetFiles,
        )
        yield _AddFiles(dataset_id=self.dataset_id, metadata=self.previous)
        yield GetDatasetFileStatus(id=self.dataset_id)
        debouncer = Debouncer()
        while not all(
            f.status in ["DOWNLOADED", "FAILED", "PROCESSED"]
            for f in self.previous.files
        ):
            yield GetDatasetFileStatus(id=self.previous.id)
            debouncer.backoff()


class _ProcessFiles(GraphQLRequest):
    query = """
    mutation (
        $datasetId: Int!, 
        $datafileIds: [Int]) {
        addDataFiles(
          datasetId: $datasetId, 
          datafileIds: $datafileIds) {
            id
            name
        }
    }
    """

    def __init__(self, dataset_id: int, datafile_ids: List[int]):
        super().__init__(
            self.query,
            variables={"datasetId": dataset_id, "datafileIds": datafile_ids,},
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

    def __init__(self, dataset_id: int, datafile_ids: List[int]):
        super().__init__(
            self.query, variables={"datasetId": dataset_id, "datafileIds": datafile_ids}
        )

    def process_response(self, response):
        return Dataset(**super().process_response(response)["addDataCsv"])


class ProcessFiles(RequestChain):
    """
    Process files associated with a dataset and add corresponding data to the dataset

    Args:
        dataset_id (int): ID of the dataset
        datafile_ids (List[str]): IDs of the datafiles to process
        wait (bool): Block while polling for status of files
        

    Returns:
        Dataset

    Raises:

    """

    def __init__(
        self, dataset_id: int, datafile_ids: List[int], wait: bool = True,
    ):
        self.dataset_id = dataset_id
        self.datafile_ids = datafile_ids
        self.wait = wait

    def requests(self):
        yield _ProcessFiles(self.dataset_id, self.datafile_ids)
        debouncer = Debouncer()
        yield GetDatasetFileStatus(id=self.dataset_id)
        if self.wait:
            while not all(
                f.status in ["PROCESSED", "FAILED"] for f in self.previous.files
            ):
                yield GetDatasetFileStatus(id=self.dataset_id)
                debouncer.backoff()


class ProcessCSV(RequestChain):
    """
    Process CSV associated with a dataset and add corresponding data to the dataset

    Args:
        dataset_id (int): ID of the dataset
        datafile_ids (List[str]): IDs of the CSV datafiles to process
        wait (bool): Block while polling for status of files

    Returns:
        Dataset

    Raises:

    """

    def __init__(self, dataset_id: int, datafile_ids: List[int], wait: bool = True):
        self.dataset_id = dataset_id
        self.datafile_ids = datafile_ids
        self.wait = wait

    def requests(self):
        yield _ProcessCSV(self.dataset_id, self.datafile_ids)
        debouncer = Debouncer()
        yield GetDatasetFileStatus(id=self.dataset_id)
        if self.wait:
            while not all(
                f.status in ["PROCESSED", "FAILED"] for f in self.previous.files
            ):
                yield GetDatasetFileStatus(id=self.dataset_id)
                debouncer.backoff()

