import concurrent.futures
import io
import json
from typing import Dict, List
from urllib.request import Request

from indico.client.request import GraphQLRequest, HTTPMethod, HTTPRequest, RequestChain
from indico.errors import IndicoInputError, IndicoRequestError

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
        files (str): A list of local filepaths to upload_file.
        streams (Dict[str, io.BufferedIOBase]): A dict of filenames to BufferedIOBase streams
            (any class that inherits BufferedIOBase is acceptable).

    Returns:
        files: storage objects to be use for further processing requests E.G. Document extraction (implicitly called)
    """

    def __init__(
        self, files: List[str] = None, streams: Dict[str, io.BufferedIOBase] = None
    ):

        if (files is None and streams is None) or (
            files is not None and streams is not None
        ):
            raise IndicoInputError("Must define one of files or streams, but not both.")

        super().__init__(
            HTTPMethod.POST, "/storage/files/store", files=files, streams=streams
        )

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
        filepaths (str): list of filepaths to upload_file
        batch_size (int): number of files to load per batch
        request_cls (HTTPRequest): Type of upload_file request: UploadDocument or UploadImage

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


class CreateStorageURLs(UploadDocument):
    """
    Upload an object stored on the Indico Platform and return only the storage URL to the object

    Args:
        files (str): list of filepaths to upload_file

    Returns:
        urls: list of storage urls to be use for further processing requests (e.g. FormExtraction)
    """

    def process_response(self, uploaded_files: List[dict]) -> List[str]:
        errors = [f["error"] for f in uploaded_files if f.get("error")]
        if errors:
            raise IndicoInputError(
                "\n".join(error for error in errors),
            )
        urls = [URL_PREFIX + f["path"] for f in uploaded_files]
        return urls


# Alias to ensure backwards compatibility
UploadImages = CreateStorageURLs


class GetDownloadUrl(GraphQLRequest):
    """
    Retrieve a signed url with a uri

    Args:
        uri (str): the storage uri prefixed by indico-file:///storage
    Returns:
        url (str): signed url of storage object
    """

    query = """
        mutation($uri: String!) {
            requestStorageDownloadUrl(uri: $uri) {
                signedUrl
            }
        }
    """

    def __init__(self, *, uri: str):
        uri = "indico-file:///storage" + uri
        super().__init__(self.query, variables={"uri": uri})

    def process_response(self, response: dict) -> str:
        response = super().process_response(response)
        return response["requestStorageDownloadUrl"]["signedUrl"]


class GetUploadURL(GraphQLRequest):
    """
    Receive a signed url for the file being uploaded

    """

    query = """
        mutation {
            requestStorageUploadUrl {
                signedUrl
                relativePath
            }
        }
    """

    def __init__(self):
        super().__init__(self.query)

    def process_response(self, response):
        response = super().process_response(response)

        return {
            "signed_url": response["requestStorageUploadUrl"]["signedUrl"],
            "relative_path": response["requestStorageUploadUrl"]["relativePath"],
        }


class UploadSignedURL(HTTPRequest):
    """
    Upload files with a signed url

    Args:
        files (str): A list of local filepaths to upload_file.
    """

    def __init__(
        self,
        signed_url: str,
        file: str,
    ):
        with open(file, "rb") as f:
            super().__init__(
                HTTPMethod.PUT, path=signed_url, data=f.read(), indico_url=False
            )


class UploadSigned(RequestChain):
    def __init__(self, file: str):
        self.file = file
        self.signed_url: str | None = None

    def requests(self):
        self.result: dict = {}
        yield GetUploadURL()

        signed_url: str = self.previous["signed_url"]
        relative_path: str = self.previous["relative_path"]

        yield UploadSignedURL(signed_url, self.file)

        # now self.previous should have the signed URL
        # You can now return filemeta
        # return the relative path and then test that we can download it by fetching a download url
        self.result[self.file] = {
            "signed_url": signed_url,
            "relative_path": relative_path,
        }
