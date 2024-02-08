# -*- coding: utf-8 -*-

import json
import jsons
import tempfile
from pathlib import Path
from typing import List

import pandas as pd
import deprecation

from indico.client.request import (
    Debouncer,
    GraphQLRequest,
    HTTPMethod,
    HTTPRequest,
    RequestChain,
)
from indico.errors import IndicoNotFound, IndicoInputError
from indico.queries.storage import UploadBatched, UploadImages
from indico.types.dataset import (
    Dataset,
    OcrEngine,
    OmnipageOcrOptionsInput,
    ReadApiOcrOptionsInput,
    OcrInputLanguage,
)


class ListDatasets(GraphQLRequest):
    """
    List all of your datasets

    Options:
        limit (int, default=100): Max number of datasets to retrieve

    Returns:
        List[Dataset]
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

    def __init__(self, *, limit: int = 100):
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
        if "dataset" not in response or not isinstance(response["dataset"], dict):
            raise IndicoNotFound("Failed to find dataset")
        return Dataset(**response["dataset"])


class GetDatasetFileStatus(GetDataset):
    """
    Get the status of dataset file upload

    Args:
        id (int): id of the dataset to query

    Returns:
        status (str): DOWNLOADED or FAILED
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

    Options:
        dataset_type (str): Type of dataset to create [TEXT, DOCUMENT, IMAGE]
        wait (bool, default=True): Wait for the dataset to upload and finish

    Returns:
        Dataset object

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
        ocr_engine: OcrEngine = None,
        omnipage_ocr_options: OmnipageOcrOptionsInput = None,
        read_api_ocr_options: ReadApiOcrOptionsInput = None,
    ):
        self.files = files
        self.name = name
        self.wait = wait
        self.dataset_type = dataset_type
        self.from_local_images = from_local_images
        self.image_filename_col = image_filename_col
        self.batch_size = batch_size
        self.ocr_engine = ocr_engine
        self.omnipage_ocr_options = omnipage_ocr_options
        self.read_api_ocr_options = read_api_ocr_options
        if omnipage_ocr_options is not None and read_api_ocr_options is not None:
            raise IndicoInputError(
                "Must supply either omnipage or readapi options but not both."
            )
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
                img_filepaths,
                batch_size=self.batch_size,
                request_cls=UploadImages,
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
        yield CreateEmptyDataset(
            name=self.name,
            dataset_type=self.dataset_type,
            readapi_ocr_options=self.read_api_ocr_options,
            omnipage_ocr_options=self.omnipage_ocr_options,
            ocr_engine=self.ocr_engine,
        )
        yield _AddFiles(dataset_id=self.previous.id, metadata=file_metadata, autoprocess=True)
        dataset_id = self.previous.id
        yield GetDatasetFileStatus(id=dataset_id)
        debouncer = Debouncer()
        if self.wait is True:
            while not all(
                [f.status in ["PROCESSED", "FAILED"] for f in self.previous.files]
            ):
                yield GetDatasetFileStatus(id=dataset_id)
                debouncer.backoff()
        yield GetDataset(id=dataset_id)


class RemoveDatasetFile(GraphQLRequest):
    """
    Remove a file from a dataset by ID.  To retrieve a list of files in a dataset,
    see `GetDatasetFileStatus`.

    Args:
        dataset_id (int): Dataset ID
        file_id (int): Datafile ID (returned by GetDatasetFileStatus)

    Returns:
        Dataset object
    """

    query = """
        mutation RemoveFile($datasetId: Int!, $fileId: Int!){
            deleteDatasetFile(datasetId: $datasetId, fileId: $fileId) {
                id
                status
            }
        }
    """

    def __init__(self, dataset_id: int, file_id: int):
        super().__init__(
            self.query,
            variables={"datasetId": dataset_id, "fileId": file_id},
        )

    def process_response(self, response):
        return Dataset(**super().process_response(response)["deleteDatasetFile"])


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
    mutation($name: String!, $datasetType: DatasetType, $config: DataConfigInput) {
        createDataset(name: $name, datasetType: $datasetType, config: $config ) {
            id
            name
        }
    }
    """

    def __init__(
        self,
        name: str,
        dataset_type: str = None,
        ocr_engine: OcrEngine = None,
        omnipage_ocr_options: OmnipageOcrOptionsInput = None,
        readapi_ocr_options: ReadApiOcrOptionsInput = None,
    ):
        if not dataset_type:
            dataset_type = "TEXT"
        config = None
        if ocr_engine is not None:
            config = {
                "ocrOptions": {
                    "ocrEngine": ocr_engine.name,
                    "omnipageOptions": omnipage_ocr_options,
                    "readapiOptions": readapi_ocr_options,
                }
            }
        super().__init__(
            self.query,
            variables={
                "name": name,
                "datasetType": dataset_type,
                "config": jsons.dump(
                    config,
                    key_transformer=jsons.KEY_TRANSFORMER_CAMELCASE,
                    strip_nulls=True,
                ),
            },
        )

    def process_response(self, response):
        return Dataset(**super().process_response(response)["createDataset"])


class _AddFiles(GraphQLRequest):
    query = """
    mutation AddFiles($datasetId: Int!, $metadata: JSONString!, $autoprocess: Boolean){
        addDatasetFiles(datasetId: $datasetId, metadataList: $metadata, autoprocess: $autoprocess) {
            id
            status
        }
    }
    """

    def __init__(self, dataset_id: int, metadata: List[str], autoprocess: bool):
        super().__init__(
            self.query,
            variables={
                "datasetId": dataset_id,
                "metadata": json.dumps(metadata),
                "autoprocess": autoprocess,
            },
        )

    def process_response(self, response):
        return Dataset(**super().process_response(response)["addDatasetFiles"])


class AddDatasetFiles(RequestChain):
    """
    Add files to a dataset.

    Args:
        dataset_id (int): ID of the dataset
        files (List[str]): List of pathnames to the dataset files

    Options:
        autoprocess (bool, default=False): Automatically process new dataset files
        wait (bool, default=True): Block while polling for status of files
        batch_size (int, default=20): Batch size for uploading files

    Returns:
        Dataset
    """

    previous = None

    def __init__(
        self,
        dataset_id: int,
        files: List[str],
        autoprocess: bool = False,
        wait: bool = True,
        batch_size: int = 20,
    ):
        self.dataset_id = dataset_id
        self.files = files
        self.wait = wait
        self.batch_size = batch_size
        self.autoprocess = autoprocess
        self.expected_statuses = (
            {"FAILED", "PROCESSED"}
            if autoprocess
            else {"DOWNLOADED", "FAILED", "PROCESSED"}
        )
        super().__init__()

    def requests(self):
        yield UploadBatched(
            files=self.files,
            batch_size=self.batch_size,
            request_cls=_UploadDatasetFiles,
        )
        yield _AddFiles(
            dataset_id=self.dataset_id,
            metadata=self.previous,
            autoprocess=self.autoprocess,
        )
        yield GetDatasetFileStatus(id=self.dataset_id)
        if self.wait:
            debouncer = Debouncer()
            while not all(f.status in self.expected_statuses for f in self.previous.files):
                yield GetDatasetFileStatus(id=self.previous.id)
                debouncer.backoff()


# Alias for backwards compatibility
AddFiles = AddDatasetFiles


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
            variables={"datasetId": dataset_id, "datafileIds": datafile_ids},
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

@deprecation.deprecated(deprecated_in="5.3",
                        details="Use AddFiles wtih autoprocess=True instead")
class ProcessFiles(RequestChain):
    """
    Process files associated with a dataset and add corresponding data to the dataset

    Args:
        dataset_id (int): ID of the dataset
        datafile_ids (List[str]): IDs of the datafiles to process
        wait (bool): Block while polling for status of files


    Returns:
        Dataset
    """

    def __init__(
        self,
        dataset_id: int,
        datafile_ids: List[int],
        wait: bool = True,
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

@deprecation.deprecated(deprecated_in="5.3",
                        details="Use AddFiles wtih autoprocess=True instead")
class ProcessCSV(RequestChain):
    """
    Process CSV associated with a dataset and add corresponding data to the dataset

    Args:
        dataset_id (int): ID of the dataset
        datafile_ids (List[str]): IDs of the CSV datafiles to process
    Options:
        wait (bool, default=True): Block while polling for status of files

    Returns:
        Dataset
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


class GetAvailableOcrEngines(GraphQLRequest):
    """
    Fetches and lists the available OCR engines
    """
    query = """query{
        ocrOptions {
            engines{
                name
            }
        }
    }"""

    def __init__(self):
        super().__init__(self.query)

    def process_response(self, response):
        engines = super().process_response(response)["ocrOptions"]["engines"]
        return [OcrEngine[e["name"]] for e in engines]

class GetOcrEngineLanguageCodes(GraphQLRequest):
    """
    Fetches and lists the available languages by name and code for the given OCR Engine

    Args:
        ocr_engine(OcrEngine): The engine to fetch for.
    """

    query = """query{
        ocrOptions {
            engines{
            name
            languages {
                name
                code
                }
            }
        }
    }"""


    def __init__(self, engine: OcrEngine):
        self.engine = engine
        super().__init__(self.query)

    def process_response(self, response):
        data = super().process_response(response)["ocrOptions"]["engines"]
        engine_laguages = next(
            x["languages"] for x in data if x["name"] == self.engine.name
        )
        return [OcrInputLanguage(**option) for option in engine_laguages]
