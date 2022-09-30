from indico.queries.storage import (
    UploadSignedSingle,
    RequestStorageDownloadUrl,
    UploadDocuments,
)
from indico.client import IndicoClient
from indico.config import IndicoConfig

host = "blob-us-west-2.us-west-2.indico-dev.indico.io"
token_path = "/home/ubuntu/Downloads/indico_api_token_blob.txt"

config = IndicoConfig(host=host, api_token_path=token_path)
client = IndicoClient(config=config)

files = ["/home/ubuntu/test-blob/test1.txt", "/home/ubuntu/test-blob/test2.txt"]
uri = "/uploads/4/c74bf4bc-cd07-4902-a945-600d99a3c07b"

res = client.call_concurrent(UploadSignedSingle, files)
# res = client.call(RequestStorageDownloadUrl(uri=uri))
print(f"{res}")
