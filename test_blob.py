from indico.client import IndicoClient
from indico.config import IndicoConfig
from indico.queries.storage import GetDownloadUrl, UploadSigned
import timeit

host = "blob-us-west-2.us-west-2.indico-dev.indico.io"
token_path = "/home/ubuntu/Downloads/indico_api_token_blob.txt"
token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZCI6MzAsInVzZXJfaWQiOjQsInVzZXJfZW1haWwiOiJqYWNvYi5hbmRlcnNvbkBpbmRpY28uaW8iLCJpYXQiOjE2NjQ0NzI3NDQsImF1ZCI6WyJpbmRpY286cmVmcmVzaF90b2tlbiJdfQ.6ObsnGKajiB9k1s4BIYXXQZvxoNvNWokh4h4rf1N_88"
config = IndicoConfig(host=host, api_token=token)
client = IndicoClient(config=config)

# jerry_file = "/home/jerry/indico/sub-workflows/834_2_3.pdf"
jerry_file = "/home/jerry/indico/sub-workflows/first_page.txt"
jacob_file = "/home/ubuntu/test_blob/test2.txt"
files = [
    "/home/ubuntu/test_blob/test1.txt",
] * 10
uri = "/uploads/4/06ae9e83-90d0-4fce-9692-78076144443c"


# res = client.call(UploadSigned(jacob_file))


# res = client.call_concurrent([UploadSigned(f) for f in files])
# res = client.call(GetDownloadUrl(uri=uri))
# print(f"{res}")


def ten_single_uploads():
    start = timeit.default_timer()
    for i in range(10):
        res = client.call(UploadSigned(jacob_file))
        print(res)
    end = timeit.default_timer()
    print(end - start)


def upload_ten_files_at_once():
    start = timeit.default_timer()
    res = client.call_concurrent([UploadSigned(f) for f in files])
    end = timeit.default_timer()
    print(end - start)
    print(res)


if __name__ == "__main__":
    # ten_single_uploads()
    upload_ten_files_at_once()
