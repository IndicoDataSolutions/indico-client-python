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

import pytest

from indico.client import IndicoClient
from indico.client.request import HTTPMethod
from indico.config import IndicoConfig
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
