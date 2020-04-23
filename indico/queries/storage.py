import json
from typing import List
from indico.client.request import HTTPMethod, HTTPRequest, RequestChain
from indico.errors import IndicoRequestError, IndicoInputError


URL_PREFIX = "indico-file:///storage"


class RetrieveStorageObject(HTTPRequest):
    """
    Retrieve an object stored on the Indico Platform 

    Results of some operations, notably DocumentExtraction can be quite large
    and are stored on disk in the Indico Platform. You need to retrieve them
    using RetrieveStorageObject.
    
    Args:
        storage_object (str or dict): either a string or dict with a url of the storage object to be retrieved. If a dict then "url" should be used as the key for the storage object url.
    
    Returns:
        contents (dict): Contents of the storage object, most often JSON
    """

    def __init__(self, storage_object):
        if type(storage_object) == dict:
            try:
                url = storage_object["url"]
            except KeyError:
                raise IndicoRequestError(
                    code="FAILURE",
                    error="Unable to retrieve result. Please check the status of the job object. If the status is \
                    'FAILURE', check the job object result for more detailed information.",
                )
        else:
            url = storage_object

        url = url.replace("indico-file://", "")
        super().__init__(method=HTTPMethod.GET, path=url)


class UploadDocument(HTTPRequest):
    """
    Upload an object stored on the Indico Platform 

    Used internally for uploading documents to indico platform for later processing
    
    Args:
        filepaths (str): list of filepaths to upload
    
    Returns:
        files: storage objects to be use for further processing requests E.G. Document extraction (implicitly called)
    """

    def __init__(self, files: List[str]):
        super().__init__(HTTPMethod.POST, "/storage/files/store", files=files)

    def process_response(self, uploaded_files: List[dict]):
        files = [
            {
                "filename": f["name"],
                "filemeta": json.dumps(
                    {
                        "path": f["path"],
                        "name": f["name"],
                        "uploadType": f["upload_type"],
                    }
                ),
            }
            for f in uploaded_files
        ]
        return files


class UploadBatched(RequestChain):
    """
    Batch uploading of files to the Indico Platform

    Args:
        filepaths (str): list of filepaths to upload
        batch_size (int): number of files to load per batch
        request_cls (HTTPRequest): Type of upload request: UploadDocument or UploadImage
    
    Returns:
        files: storage objects for further processing, e.g. Document extraction or dataset creation
    """

    def __init__(
        self,
        files: List[str],
        batch_size: int = 20,
        request_cls: HTTPRequest = UploadDocument,
    ):
        self.result = None
        self.files = files
        self.batch_size = batch_size
        self.request_cls = request_cls

    def requests(self):
        self.result = []
        for i in range(0, len(self.files), self.batch_size):
            yield self.request_cls(self.files[i : i + self.batch_size])
            self.result.extend(self.previous)


class UploadImages(UploadDocument):
    """
    Upload image files stored on a local filepath to the indico platform.
    """

    def process_response(self, uploaded_files: List[dict]) -> List[str]:
        errors = [f["error"] for f in uploaded_files if f.get("error")]
        if errors:
            return IndicoInputError(error="\n".join(error for error in errors),)
        urls = [URL_PREFIX + f["path"] for f in uploaded_files]
        return urls
