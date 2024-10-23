import requests

from indico.client.request import GraphQLRequest
from indico.errors import IndicoRequestError
from indico.types.jobs import Job


class ProcessStaticModelExport(GraphQLRequest):
    """
    Process a static model export.

    Available on 6.14+ only.

    Args:
        storage_uri(str): the storage uri of the static model export that was uploaded to Indico.

    Returns:
        Job: the job that was created to process the static model export.
    """

    query = """
        mutation processStaticModelExport($storageUri: String!) {
            processStaticModelExport(storageUri: $storageUri) {
                jobId
            }
        }
    """

    def __init__(self, storage_uri: str):
        super().__init__(self.query, variables={"storageUri": storage_uri})

    def process_response(self, response) -> Job:
        job_id = super().process_response(response)["processStaticModelExport"]["jobId"]
        return Job(id=job_id)


class UploadStaticModelExport(GraphQLRequest):
    """
    Upload a static model export to Indico.

    Available on 6.14+ only.

    Args:
        file_path(str): path to the export zip file to upload to Indico.

    Returns:
        str: the storage uri of the static model export.
    """

    query = """
        query exportUpload {
            exportUpload {
                signedUrl
                storageUri
            }
        }
    """

    def __init__(self, file_path: str):
        self.file_path = file_path
        super().__init__(self.query)

    def process_response(self, response) -> str:
        resp = super().process_response(response)["exportUpload"]
        signed_url = resp["signedUrl"]
        storage_uri = resp["storageUri"]

        with open(self.file_path, "rb") as file:
            file_content = file.read()

        headers = {"Content-Type": "application/zip"}
        response = requests.put(signed_url, data=file_content, headers=headers)

        if response.status_code != 200:
            raise IndicoRequestError(
                f"Failed to upload static model export: {response.text}"
            )

        return storage_uri
