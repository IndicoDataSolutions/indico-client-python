import json
from typing import List
from indico.client.request import RequestChain, GraphQLRequest, HTTPMethod, HTTPRequest
from indico.types.jobs import Job


class _UploadDocument(HTTPRequest):
    def __init__(self, files: List[str]):
        super().__init__(HTTPMethod.POST, "/storage/files/store", files=files)
    
    def process_response(self, uploaded_files: List[dict]):
        files =  [
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
    query ="""
        mutation($files: [FileInput], $jsonConfig: JSONString) {
            documentExtraction(files: $files, jsonConfig: $jsonConfig ) {
                jobIds
            }
        }
    """

    def __init__(self, files, json_config={"preset_config": "simple"}):
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
    def __init__(self, files: List[str], json_config: dict=None):
        self.files = files
        self.json_config = json_config
    
    def requests(self):
        yield _UploadDocument(files=self.files)
        yield _DocumentExtraction(files=self.previous, json_config=self.json_config)