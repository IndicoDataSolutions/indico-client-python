from indico.client import IndicoClient
from indico.config import IndicoConfig
from indico.queries.storage import RequestStorageDownloadUrl, UploadSigned

host = "blob-us-west-2.us-west-2.indico-dev.indico.io"
token_path = "/home/ubuntu/Downloads/indico_api_token_blob.txt"
token = ""
config = IndicoConfig(host=host, api_token=token)
client = IndicoClient(config=config)

jerry_file = "/home/jerry/indico/sub-workflows/834_2_3.pdf"
files = [
    "/home/jerry/indico/sub-workflows/834_2_3.pdf",
    "/home/ubuntu/test-blob/test2.txt",
]
uri = "/uploads/4/c74bf4bc-cd07-4902-a945-600d99a3c07b"


res = client.call(UploadSigned(jerry_file))

# res = client.call_concurrent([UploadSigned(f) for f in files])
# res = client.call(RequestStorageDownloadUrl(uri=uri))
print(f"{res}")
