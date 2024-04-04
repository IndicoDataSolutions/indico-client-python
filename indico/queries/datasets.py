# -*- coding: utf-8 -*-

import json
import tempfile
from pathlib import Path
from typing import TYPE_CHECKING

import jsons
import pandas as pd

from indico.client.request import (
    Delay,
    GraphQLRequest,
    HTTPMethod,
    HTTPRequest,
    PagedRequest,
    RequestChain,
)
from indico.errors import IndicoInputError, IndicoNotFound
from indico.filters import DatasetFilter
from indico.queries.storage import UploadBatched, UploadImages
from indico.types.dataset import Dataset, OcrEngine, OcrInputLanguage

if TYPE_CHECKING:  # pragma: no cover
    from typing import Iterator, List, Optional, Union

    from indico.types.dataset import OmnipageOcrOptionsInput, ReadApiOcrOptionsInput
    from indico.typing import AnyDict, Payload


class ListDatasets(PagedRequest["List[Dataset]"]):
    """
    List all of your datasets

    Options:
        limit (int, default=100): Max number of datasets to retrieve

    Returns:
        List[Dataset]
    """

    query = """
        query ListDatasets(
            $filters: DatasetFilter,
            $limit: Int,
            $orderBy: DATASET_COLUMN_ENUM,
            $desc: Boolean,
            $after: Int
        ){
            datasetsPage(
                filters: $filters,
                limit: $limit
                orderBy: $orderBy,
                desc: $desc,
                after: $after
            ) {
                datasets {
                    id
                    name
                    rowCount
                }
                pageInfo {
                    hasNextPage
                    endCursor
                }
            }
        }
    """

    def __init__(
        self,
        *,
        filters: "Optional[Union[AnyDict, DatasetFilter]]" = None,
        limit: int = 100,
        order_by: str = "ID",
        desc: bool = False,
    ):
        super().__init__(
            self.query,
            variables={
                "filters": filters,
                "limit": limit,
                "orderBy": order_by,
                "desc": desc,
            },
        )

    def process_response(self, response: "Payload") -> "List[Dataset]":
        response = super().parse_payload(response)
        return [Dataset(**dataset) for dataset in response["datasetsPage"]["datasets"]]


class GetDataset(GraphQLRequest["Dataset"]):
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

    def process_response(self, response: "Payload") -> "Dataset":
        response = super().parse_payload(response)
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


class GetDatasetStatus(GraphQLRequest[str]):
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

    def process_response(self, response: "Payload") -> str:
        status: str = super().parse_payload(response)["dataset"]["status"]
        return status


class CreateDataset(RequestChain["Dataset"]):
    """
    Create a dataset and upload the associated files.

    Args:
        name (str): Name of the dataset.
        files (List[str]): List of path names to the dataset files.
        wait (bool, optional): Wait for the dataset to upload and finish. Defaults to True.
        dataset_type (str, optional): Type of dataset to create [TEXT, DOCUMENT, IMAGE]. Defaults to TEXT.
        from_local_images (bool, optional): Flag whether files are local images or not. Defaults to False.
        image_filename_col (str, optional): Image filename column. Defaults to 'filename'.
        batch_size (int, optional): Size of file batch to upload at a time. Defaults to 20.
        ocr_engine (OcrEngine, optional): Specify an OCR engine [OMNIPAGE, READAPI, READAPI_V2, READAPI_TABLES_V1]. Defaults to None.
        omnipage_ocr_options (OmnipageOcrOptionsInput, optional): If using Omnipage, specify Omnipage OCR options. Defaults to None.
        read_api_ocr_options: (ReadApiOcrOptionsInput, optional): If using ReadAPI, specify ReadAPI OCR options. Defaults to None.
        request_interval (int or float, optional): The maximum time in between retry calls when waiting. Defaults to 5 seconds.

    Returns:
        Dataset object

    """

    def __init__(
        self,
        name: str,
        files: "Union[str, List[str]]",
        wait: bool = True,
        dataset_type: str = "TEXT",
        from_local_images: bool = False,
        image_filename_col: str = "filename",
        batch_size: int = 20,
        ocr_engine: "Optional[OcrEngine]" = None,
        omnipage_ocr_options: "Optional[OmnipageOcrOptionsInput]" = None,
        read_api_ocr_options: "Optional[ReadApiOcrOptionsInput]" = None,
        request_interval: "Union[int, float]" = 5,
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
        self.request_interval = request_interval
        if omnipage_ocr_options is not None and read_api_ocr_options is not None:
            raise IndicoInputError(
                "Must supply either omnipage or readapi options but not both."
            )
        super().__init__()

    def requests(
        self,
    ) -> "Iterator[Union[UploadBatched, _UploadDatasetFiles, CreateEmptyDataset, _AddFiles, GetDatasetFileStatus, Delay, GetDataset]]":
        if self.from_local_images:
            if not isinstance(self.files, str):
                raise ValueError(
                    "'files' should be a string path when using `from_local_images`."
                )

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
            if not isinstance(self.files, list):
                raise ValueError("'files' should be a list of paths.")

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
        yield _AddFiles(
            dataset_id=self.previous.id, metadata=file_metadata, autoprocess=True
        )
        dataset_id = self.previous.id
        yield GetDatasetFileStatus(id=dataset_id)
        if self.wait is True:
            while not all(
                [f.status in ["PROCESSED", "FAILED"] for f in self.previous.files]
            ):
                yield GetDatasetFileStatus(id=dataset_id)
                yield Delay(seconds=self.request_interval)
        yield GetDataset(id=dataset_id)


class RemoveDatasetFile(GraphQLRequest["Dataset"]):
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

    def process_response(self, response: "Payload") -> "Dataset":
        return Dataset(**super().parse_payload(response)["deleteDatasetFile"])


class _UploadDatasetFiles(HTTPRequest["List[AnyDict]"]):
    def __init__(self, files: "List[str]"):
        super().__init__(
            method=HTTPMethod.POST, path="/storage/files/upload", files=files
        )


class DeleteDataset(GraphQLRequest[bool]):
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

    def __init__(self, id: int):
        super().__init__(self.query, variables={"id": id})

    def process_response(self, response: "Payload") -> bool:
        status: bool = super().parse_payload(response)["deleteDataset"]["success"]
        return status


class CreateEmptyDataset(GraphQLRequest["Dataset"]):
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
        dataset_type: "Optional[str]" = None,
        ocr_engine: "Optional[OcrEngine]" = None,
        omnipage_ocr_options: "Optional[OmnipageOcrOptionsInput]" = None,
        readapi_ocr_options: "Optional[ReadApiOcrOptionsInput]" = None,
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

    def process_response(self, response: "Payload") -> "Dataset":
        return Dataset(**super().parse_payload(response)["createDataset"])


class _AddFiles(GraphQLRequest["Dataset"]):
    query = """
    mutation AddFiles($datasetId: Int!, $metadata: JSONString!, $autoprocess: Boolean){
        addDatasetFiles(datasetId: $datasetId, metadataList: $metadata, autoprocess: $autoprocess) {
            id
            status
        }
    }
    """

    def __init__(self, dataset_id: int, metadata: "List[str]", autoprocess: bool):
        super().__init__(
            self.query,
            variables={
                "datasetId": dataset_id,
                "metadata": json.dumps(metadata),
                "autoprocess": autoprocess,
            },
        )

    def process_response(self, response: "Payload") -> "Dataset":
        return Dataset(**super().parse_payload(response)["addDatasetFiles"])


class AddDatasetFiles(RequestChain["Dataset"]):
    """
    Add files to a dataset.

    Args:
        dataset_id (int): ID of the dataset
        files (List[str]): List of pathnames to the dataset files

    Options:
        autoprocess (bool, default=True): Automatically process new dataset files
        wait (bool, default=True): Block while polling for status of files
        batch_size (int, default=20): Batch size for uploading files

    Returns:
        Dataset
    """

    def __init__(
        self,
        dataset_id: int,
        files: "List[str]",
        autoprocess: bool = True,
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

    def requests(
        self,
    ) -> "Iterator[Union[UploadBatched, _AddFiles, GetDatasetFileStatus, Delay]]":
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
            while not all(
                f.status in self.expected_statuses for f in self.previous.files
            ):
                yield Delay()
                yield GetDatasetFileStatus(id=self.previous.id)


# Alias for backwards compatibility
AddFiles = AddDatasetFiles


class GetAvailableOcrEngines(GraphQLRequest["List[OcrEngine]"]):
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

    def __init__(self) -> None:
        super().__init__(self.query)

    def process_response(self, response: "Payload") -> "List[OcrEngine]":
        engines = super().parse_payload(response)["ocrOptions"]["engines"]
        return [OcrEngine[e["name"]] for e in engines]


class GetOcrEngineLanguageCodes(GraphQLRequest["List[OcrInputLanguage]"]):
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

    def __init__(self, engine: "OcrEngine"):
        self.engine = engine
        super().__init__(self.query)

    def process_response(self, response: "Payload") -> "List[OcrInputLanguage]":
        data = super().parse_payload(response)["ocrOptions"]["engines"]
        engine_laguages = next(
            x["languages"] for x in data if x["name"] == self.engine.name
        )
        return [OcrInputLanguage(**option) for option in engine_laguages]
