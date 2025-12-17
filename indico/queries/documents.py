# -*- coding: utf-8 -*-

import json
from typing import TYPE_CHECKING

from indico.client.request import GraphQLRequest, RequestChain
from indico.queries.storage import UploadBatched, UploadDocument
from indico.types.jobs import Job

if TYPE_CHECKING:  # pragma: no cover
    from typing import Iterator, List, Optional, Union

    from indico.typing import AnyDict, Payload


class _DocumentExtraction(GraphQLRequest["List[Job]"]):
    query = """
        mutation($files: [FileInput], $jsonConfig: JSONString, $ocrEngine: OCREngine) {
            documentExtraction(files: $files, jsonConfig: $jsonConfig, ocrEngine: $ocrEngine) {
                jobIds
            }
        }
    """

    def __init__(
        self,
        files: "List[AnyDict]",
        json_config: "Optional[Union[AnyDict, str]]" = {"preset_config": "legacy"},
        ocr_engine: "Optional[str]" = None,
    ):
        json_config_json: "Optional[str]" = None
        if json_config:
            if isinstance(json_config, dict):
                json_config_json = json.dumps(json_config)
            else:
                json_config_json = json_config

        super().__init__(
            query=self.query,
            variables={
                "files": files,
                "jsonConfig": json_config_json,
                "ocrEngine": ocr_engine,
            },
        )

    def process_response(self, response: "Payload") -> "List[Job]":
        jobs = super().parse_payload(response)["documentExtraction"]["jobIds"] or set()
        return [Job(id=j) for j in jobs]


class DocumentExtraction(RequestChain["Job"]):
    """
    Extract raw text from PDF or TIF files.

    DocumentExtraction performs Optical Character Recognition (OCR) on PDF or TIF files to
    extract raw text for model training and prediction.

    Args:
        files= (List[str]): Pathnames of one or more files to OCR
        json_config (dict or JSON str): Configuration settings for OCR. See Notes below.
        upload_batch_size (int): Size of batches for document upload if uploading many documents
        ocr_engine (str): Denotes which ocr engine to use. Defaults to OMNIPAGE.

    Returns:
        Job object

    Notes:
        DocumentExtraction is extremely configurable. Four preset configurations are provided:

        simple - Provides a simple and fast response for native PDFs (3-5x faster). Will NOT work with scanned PDFs.

        legacy - Provided to mimic the behavior of Indico's older pdf_extraction function. Use this if your model was trained with data from the older pdf_extraction.

        detailed - Provides detailed bounding box information on tokens and characters. Returns data in a nested format at the document level with all metadata included.

        ondocument - Provides detailed information at the page-level in an unnested format.

        standard - Provides page text and block text/position in a nested format.

        For more information, please reference the Indico knowledgebase article on OCR:
        https://docs.indicodata.ai/articles/documentation-publication/ocr
    """

    def __init__(
        self,
        files: "List[str]",
        json_config: "Optional[AnyDict]" = None,
        upload_batch_size: "Optional[int]" = None,
        ocr_engine: str = "OMNIPAGE",
    ):
        self.files = files
        self.json_config = json_config
        self.upload_batch_size = upload_batch_size
        self.ocr_engine = ocr_engine

    def requests(
        self,
    ) -> "Iterator[Union[UploadBatched, UploadDocument, _DocumentExtraction]]":
        if self.upload_batch_size:
            yield UploadBatched(
                files=self.files,
                batch_size=self.upload_batch_size,
                request_cls=UploadDocument,
            )
        else:
            yield UploadDocument(files=self.files)

        yield _DocumentExtraction(
            files=self.previous,
            json_config=self.json_config,
            ocr_engine=self.ocr_engine,
        )
