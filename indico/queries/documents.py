# -*- coding: utf-8 -*-

import json
from typing import List

from indico.client.request import RequestChain, GraphQLRequest, HTTPMethod, HTTPRequest
from indico.types.jobs import Job
from indico.queries.storage import UploadDocument, UploadBatched


class _DocumentExtraction(GraphQLRequest):

    query = """
        mutation($files: [FileInput], $jsonConfig: JSONString) {
            documentExtraction(files: $files, jsonConfig: $jsonConfig ) {
                jobIds
            }
        }
    """

    def __init__(self, files, json_config={"preset_config": "legacy"}):
        if json_config and type(json_config) == dict:
            json_config = json.dumps(json_config)
        super().__init__(
            query=self.query, variables={"files": files, "jsonConfig": json_config}
        )

    def process_response(self, response):
        jobs = super().process_response(response)["documentExtraction"]["jobIds"]
        if jobs:
            return [Job(id=j) for j in jobs]
        else:
            return []


class DocumentExtraction(RequestChain):
    """
    Extract raw text from PDF or TIF files.

    DocumentExtraction performs Optical Character Recognition (OCR) on PDF or TIF files to
    extract raw text for model training and prediction.

    Args:
        files= (List[str]): Pathnames of one or more files to OCR
        json_config (dict or JSON str): Configuration settings for OCR. See Notes below.
        upload_batch_size (int): size of batches for document upload if uploading many documents

    Returns:
        Job object

    Raises:

    Notes:
        DocumentExtraction is extremely configurable. Four preset configurations are provided:

        simple - Provides a simple and fast response for native PDFs (3-5x faster). Will NOT work with scanned PDFs.

        legacy - Provided to mimic the behavior of Indico's older pdf_extraction function. Use this if your model was trained with data from the older pdf_extraction.

        detailed - Provides detailed bounding box information on tokens and characters. Returns data in a nested format at the document level with all metadata included.

        ondocument - Provides detailed information at the page-level in an unnested format.

        standard - Provides page text and block text/position in a nested format.

        For more information, please see the DocumentExtraction settings page.

    Example:

        Call DocumentExtraction and wait for the result::

            job = client.call(DocumentExtraction(files=[src_path], json_config='{"preset_config": "legacy"}'))
            job = client.call(JobStatus(id=job[0].id, wait=True))
            extracted_data = client.call(RetrieveStorageObject(job.result))
    """

    def __init__(
        self, files: List[str], json_config: dict = None, upload_batch_size: int = None
    ):
        self.files = files
        self.json_config = json_config
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
        yield _DocumentExtraction(files=self.previous, json_config=self.json_config)
