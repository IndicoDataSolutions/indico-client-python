# -*- coding: utf-8 -*-

import json
from typing import List

from indico.client.request import RequestChain, GraphQLRequest, HTTPMethod, HTTPRequest
from indico.types.jobs import Job


class _UploadDocument(HTTPRequest):
    def __init__(self, files: List[str]):
        super().__init__(HTTPMethod.POST, "/storage/files/store", files=files)
    
    def process_response(self, uploaded_files: List[dict]):
        files = [
            {
                "filename": f["name"],
                "filemeta": json.dumps(
                    {"path": f["path"], "name": f["name"], "uploadType": f["upload_type"]}
                ),
            }
            for f in uploaded_files
        ]
        return files


class _DocumentExtraction(GraphQLRequest):
    
    query = """
        mutation($files: [FileInput], $jsonConfig: JSONString) {
            documentExtraction(files: $files, jsonConfig: $jsonConfig ) {
                jobIds
            }
        }
    """

    def __init__(self, files, json_config={"preset_config": "simple"}):
        if json_config and type(json_config) == dict:
            json_config = json.dumps(json_config)
        super().__init__(query=self.query, variables={
            "files": files,
            "jsonConfig": json_config
        })

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

    Returns:
        Job object

    Raises:

    Notes:
        DocumentExtraction is extremely configurable. Three preset configurations are provided:

        simple - Most applications won't need more than this.

        legacy - Provided to mimic the behavior of Indico's older pdf_extraction function. Use this if your model was trained with data from pdf_extraction.
        
        detailed - Provides detailed bounding box information on tokens and characters.

        For more information, please see the DocumentExtraction settings page.

    Example:

        Call DocumentExtraction and wait for the result::

            job = client.call(DocumentExtraction(files=[src_path], json_config='{"preset_config": "simple"}'))
            job = client.call(JobStatus(id=job[0].id, wait=True))
            if job is not None and job.status == 'SUCCESS':
                json_data = client.call(RetrieveStorageObject(job.result))
                print(json.dumps(json_data, indent=4))
    """

    def __init__(self, files: List[str], json_config: dict=None):
        self.files = files
        self.json_config = json_config
    
    def requests(self):
        yield _UploadDocument(files=self.files)
        yield _DocumentExtraction(files=self.previous, json_config=self.json_config)