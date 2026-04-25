"""
Storage-service compatibility unit tests.

Validates that Python SDK storage query classes remain compatible with the
response shapes produced by storage-service (the Rainbow replacement).  These
tests mock at the HTTP level and require no running service.

Covered flows:
  * UploadDocument: POST /storage/files/store, LegacyUploadResponseItem shape
  * CreateStorageURLs: indico-file:///storage<path> URI construction
  * RetrieveStorageObject: indico-file:// prefix stripping and GET path
"""

import io
import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

import pytest

from indico.client import IndicoClient
from indico.client.request import HTTPMethod
from indico.config import IndicoConfig
from indico.errors import IndicoRequestError
from indico.queries.model_import import _UploadSMExport
from indico.queries.storage import (
    CreateStorageURLs,
    RetrieveStorageObject,
    UploadDocument,
)

# ---------------------------------------------------------------------------
# Response shape produced by storage-service /files/store endpoint
# (mirrors LegacyUploadResponseItem from storage_service/routes/blob_routes.py)
# ---------------------------------------------------------------------------
STORAGE_SERVICE_UPLOAD_RESPONSE = [
    {
        "path": "/uploads/42/abc-uuid",
        "name": "document.pdf",
        "size": 12345,
        "upload_type": "user",
    }
]


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def cfg():
    return IndicoConfig(protocol="mock", host="mock")


@pytest.fixture
def mock_request(requests_mock, cfg):
    """Register a URL on requests_mock using the test config base URL."""

    def _register(method, path, **kwargs):
        url = f"{cfg.protocol}://{cfg.host}{path}"
        getattr(requests_mock, method)(
            url, **kwargs, headers={"Content-Type": "application/json"}
        )

    return _register


@pytest.fixture
def client(mock_request, cfg):
    mock_request("post", "/auth/users/refresh_token", json={"auth_token": "tok"})
    return IndicoClient(config=cfg)


# ---------------------------------------------------------------------------
# UploadDocument — request shape and response parsing
# ---------------------------------------------------------------------------


def test_upload_document_posts_to_storage_files_store(mock_request, client):
    """UploadDocument sends POST to /storage/files/store."""
    captured = []

    def capture(request, context):
        captured.append(request.path)
        context.status_code = 200
        context.headers["Content-Type"] = "application/json"
        import json as _json

        return _json.dumps(STORAGE_SERVICE_UPLOAD_RESPONSE)

    mock_request("post", "/storage/files/store", text=capture)
    client.call(UploadDocument(streams={"test.pdf": io.BytesIO(b"data")}))
    assert captured == ["/storage/files/store"]


def test_upload_document_processes_path_name_upload_type(mock_request, client):
    """UploadDocument.process_response reads path/name/upload_type from storage-service."""
    mock_request("post", "/storage/files/store", json=STORAGE_SERVICE_UPLOAD_RESPONSE)
    result = client.call(UploadDocument(streams={"test.pdf": io.BytesIO(b"data")}))

    assert len(result) == 1
    assert result[0]["filename"] == "document.pdf"
    meta = json.loads(result[0]["filemeta"])
    assert meta["path"] == "/uploads/42/abc-uuid"
    assert meta["name"] == "document.pdf"
    assert meta["uploadType"] == "user"


def test_upload_document_handles_multiple_files(mock_request, client):
    """Multiple files in one upload are each parsed correctly."""
    multi_response = [
        {
            "path": "/uploads/42/uuid-1",
            "name": "a.pdf",
            "size": 100,
            "upload_type": "user",
        },
        {
            "path": "/uploads/42/uuid-2",
            "name": "b.pdf",
            "size": 200,
            "upload_type": "user",
        },
    ]
    mock_request("post", "/storage/files/store", json=multi_response)
    result = client.call(
        UploadDocument(
            streams={
                "a.pdf": io.BytesIO(b"aaa"),
                "b.pdf": io.BytesIO(b"bbb"),
            }
        )
    )
    assert len(result) == 2
    assert result[0]["filename"] == "a.pdf"
    assert result[1]["filename"] == "b.pdf"


# ---------------------------------------------------------------------------
# CreateStorageURLs — indico-file URI construction
# ---------------------------------------------------------------------------


def test_create_storage_urls_builds_indico_file_uris(mock_request, client):
    """CreateStorageURLs returns indico-file:///storage<path> from storage-service response."""
    mock_request("post", "/storage/files/store", json=STORAGE_SERVICE_UPLOAD_RESPONSE)
    result = client.call(CreateStorageURLs(streams={"test.pdf": io.BytesIO(b"data")}))
    assert result == ["indico-file:///storage/uploads/42/abc-uuid"]


def test_create_storage_urls_round_trips_through_retrieve(mock_request, client):
    """A URI from CreateStorageURLs can be fed directly into RetrieveStorageObject."""
    uri = "indico-file:///storage/uploads/42/abc-uuid"
    req = RetrieveStorageObject(uri)
    assert req.path == "/storage/uploads/42/abc-uuid"
    assert req.method == HTTPMethod.GET


# ---------------------------------------------------------------------------
# RetrieveStorageObject — path construction
# ---------------------------------------------------------------------------


def test_retrieve_storage_object_strips_indico_file_scheme():
    """indico-file:// prefix is stripped; remaining path becomes the GET path."""
    req = RetrieveStorageObject("indico-file:///storage/submissions/1/2/result.json")
    assert req.path == "/storage/submissions/1/2/result.json"
    assert req.method == HTTPMethod.GET


def test_retrieve_storage_object_accepts_dict_with_url_key():
    """Accepts a dict with 'url' key (as returned by GraphQL result objects)."""
    req = RetrieveStorageObject({"url": "indico-file:///storage/extractions/99.json"})
    assert req.path == "/storage/extractions/99.json"


def test_retrieve_storage_object_fetches_content(mock_request, client):
    """GET /storage/<path> is issued and the response body is returned."""
    payload = {"status": "complete", "results": [{"text": "hello"}]}
    mock_request("get", "/storage/submissions/1/2/result.json", json=payload)
    result = client.call(
        RetrieveStorageObject("indico-file:///storage/submissions/1/2/result.json")
    )
    assert result == payload


def test_retrieve_storage_object_follows_redirects():
    """Storage GET requests follow redirects in redirect-mode deployments."""
    payload = {"status": "complete", "results": [{"text": "redirected"}]}
    refresh_path = "/auth/users/refresh_token"
    source_path = "/storage/submissions/1/2/result.json"
    redirected_path = "/storage/signed/submissions/1/2/result.json"

    class Handler(BaseHTTPRequestHandler):
        def do_POST(self):  # noqa: N802
            if self.path != refresh_path:
                self.send_response(404)
                self.end_headers()
                return
            body = json.dumps({"auth_token": "tok"}).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):  # noqa: N802
            if self.path == source_path:
                self.send_response(302)
                self.send_header(
                    "Location",
                    f"http://{self.server.server_address[0]}:{self.server.server_address[1]}{redirected_path}",
                )
                self.end_headers()
                return
            if self.path == redirected_path:
                body = json.dumps(payload).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
                return
            self.send_response(404)
            self.end_headers()

        def log_message(self, format, *args):  # noqa: A003
            return

    with HTTPServer(("127.0.0.1", 0), Handler) as server:
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            host = f"{server.server_address[0]}:{server.server_address[1]}"
            client = IndicoClient(config=IndicoConfig(protocol="http", host=host))
            result = client.call(
                RetrieveStorageObject(
                    "indico-file:///storage/submissions/1/2/result.json"
                )
            )
            assert result == payload
        finally:
            server.shutdown()
            thread.join(timeout=5)


def test_upload_static_model_export_puts_zip_to_signed_url(tmp_path, requests_mock):
    """Static model export upload uses the signed URL with zip content-type."""
    export_path = tmp_path / "model.zip"
    export_bytes = b"zip-bytes"
    export_path.write_bytes(export_bytes)
    signed_url = "https://signed.example/upload"
    storage_uri = "indico-file:///storage/exports/model.zip"

    requests_mock.put(signed_url, status_code=200, text="")

    request = _UploadSMExport(str(export_path))
    result = request.process_response(
        {"data": {"exportUpload": {"signedUrl": signed_url, "storageUri": storage_uri}}}
    )

    assert result == storage_uri
    assert len(requests_mock.request_history) == 1
    put_call = requests_mock.request_history[0]
    assert put_call.method == "PUT"
    assert put_call.headers["Content-Type"] == "application/zip"
    assert put_call.body == export_bytes


def test_upload_static_model_export_raises_on_put_failure(tmp_path, requests_mock):
    """A failing signed-url PUT raises IndicoRequestError."""
    export_path = tmp_path / "model.zip"
    export_path.write_bytes(b"zip-bytes")
    signed_url = "https://signed.example/upload"

    requests_mock.put(signed_url, status_code=403, text="forbidden")

    request = _UploadSMExport(str(Path(export_path)))
    with pytest.raises(IndicoRequestError):
        request.process_response(
            {
                "data": {
                    "exportUpload": {
                        "signedUrl": signed_url,
                        "storageUri": "indico-file:///storage/exports/model.zip",
                    }
                }
            }
        )
