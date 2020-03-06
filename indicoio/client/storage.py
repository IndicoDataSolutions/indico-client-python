from indicoio.client.client import RequestProxy
from typing import List
from pathlib import Path
import uuid
import simplejson as json
import io
import gzip


class StorageClient(RequestProxy):
    def upload(self, data: List[str]):
        """
        Calls user upload endpoint and returns the FileInput formatted representations
        """
        files = {}
        for datum in data:
            path = Path(datum)
            if path.exists():
                files[path.stem] = path.open("rb")
            else:
                files[str(uuid.uuid4())] = datum

        uploaded_files = self.post("/storage/files/store", files=files)
        return _parse_uploaded_files(uploaded_files)

    def download(self, url: str):
        storage_url = _resolve_indico_protocol(self.base_url, url)
        response = self.request_session.get(
            storage_url, stream=True, headers={"Accept-Encoding": "gzip, deflate"}
        )
        response.raw.decode_content = True
        value = io.BytesIO(response.raw.data).getvalue()
        if url.split(".")[-1] == "json":
            return json.loads(value)
        elif url.split(".")[-1] == "gz":
            return json.loads(gzip.decompress(value))
        else:
            return value


def _parse_uploaded_files(uploaded_files: List[dict]):
    return [
        {
            "filename": f["name"],
            "filemeta": json.dumps(
                {"path": f["path"], "name": f["name"], "uploadType": f["upload_type"]}
            ),
        }
        for f in uploaded_files
    ]


def _resolve_indico_protocol(base_url, url):
    relative_url = "/".join(url.split("/")[3:])
    full_url = f"{base_url}/api/storage/" + relative_url
    return full_url
