import json
from pathlib import Path
from typing import Any, Dict, List, Optional

import pytest
import requests_mock as requests_mock_lib

from indico.client import AsyncIndicoClient, IndicoClient
from indico.errors import IndicoInputError, IndicoRequestError
from indico.queries.field_blueprints import (
    DownloadFieldBlueprintExport,
    ExportFieldBlueprints,
    UploadFieldBlueprints,
)
from indico.types.jobs import Job
from tests.fixtures.graphql import (
    HTML_HEADERS,
    JSON_HEADERS,
    RAINBOW_LIST,
    graphql_responses,
)
from tests.fixtures.transport import FakeAioResponse, FakeAioSession

NAME = "9b2d7c1e-3f4a-4b5c-8d6e-7f8a9b0c1d2e.json"
UPLOAD_PATH = "/storage/fields/blueprints/import/upload"
UPLOAD_URL = f"{UPLOAD_PATH}?name={NAME}"
UPLOAD_PROXY_URL = f"mock://mock{UPLOAD_PATH}"
STORAGE_URI = f"indico-file:///storage/fields/blueprints/import/{NAME}"
EXPORT_NAME = "blueprint_export_4c5d6e7f-8a9b-4c0d-9e1f-2a3b4c5d6e7f.json"
DOWNLOAD_URL = f"/storage/fields/blueprints/export/{EXPORT_NAME}"
DOWNLOAD_PROXY_URL = f"mock://mock{DOWNLOAD_URL}"
OCTET_HEADERS = {"Content-Type": "application/octet-stream"}
EXPORT_BODY = {"blueprints": [{"uid": "b1", "name": "Invoice Date"}]}
EXPORT_RESULT = {
    "count": 1,
    "download_url": DOWNLOAD_URL,
    "filename": EXPORT_NAME,
    "storage_uri": f"indico-file:///storage/fields/blueprints/export/{EXPORT_NAME}",
}


def upload_payload(upload_url: Optional[str]) -> Dict[str, Any]:
    return {
        "data": {
            "getImportUploadSignedUrl": {
                "uploadUrl": upload_url,
                "storageUri": STORAGE_URI,
            }
        }
    }


def job_payload(status: str, result: Any) -> Dict[str, Any]:
    return {
        "data": {
            "job": {
                "id": "j1",
                "ready": True,
                "status": status,
                "result": json.dumps(result),
            }
        }
    }


def finished_job(status: str, result: Any) -> Job:
    return Job(id="j1", ready=True, status=status, result=json.dumps(result))


def transfers(requests_mock: requests_mock_lib.Mocker, path: str) -> List[Any]:
    return [r for r in requests_mock.request_history if r.path == path]


@pytest.fixture
def blueprint_path(tmp_path: Path) -> str:
    path = tmp_path / "blueprints.json"
    path.write_bytes(b'{"blueprints": []}')
    return str(path)


def test_upload_proxied(
    client: IndicoClient,
    requests_mock: requests_mock_lib.Mocker,
    blueprint_path: str,
) -> None:
    graphql = graphql_responses(requests_mock, upload_payload(UPLOAD_URL))
    proxy = requests_mock.post(
        UPLOAD_PROXY_URL, json=RAINBOW_LIST, headers=JSON_HEADERS
    )

    assert client.call(UploadFieldBlueprints(file_path=blueprint_path)) == STORAGE_URI
    query = graphql.last_request.json()["query"]
    assert "getImportUploadSignedUrl" in query
    assert "uploadUrl" in query
    assert "signedUrl" not in query
    assert "auth_token=tok" in proxy.request_history[-1].headers["Cookie"]
    assert proxy.request_history[-1].qs == {"name": [NAME]}
    assert b'filename="blueprints.json"' in proxy.request_history[-1].body
    assert b'{"blueprints": []}' in proxy.request_history[-1].body


@pytest.mark.parametrize(
    "upload_url, match",
    [
        (None, "upload URL"),
        (f"https://h{UPLOAD_URL}", "Unexpected storage URL"),
        (f"/files{UPLOAD_PATH}", "Unexpected storage URL"),
    ],
)
def test_upload_refuses_bad_upload_url(
    client: IndicoClient,
    requests_mock: requests_mock_lib.Mocker,
    blueprint_path: str,
    upload_url: Optional[str],
    match: str,
) -> None:
    graphql = graphql_responses(requests_mock, upload_payload(upload_url))

    with pytest.raises(IndicoRequestError, match=match):
        client.call(UploadFieldBlueprints(file_path=blueprint_path, auto_import=True))
    assert graphql.call_count == 1
    assert transfers(requests_mock, UPLOAD_PATH) == []


def test_upload_does_not_follow_redirects(
    client: IndicoClient,
    requests_mock: requests_mock_lib.Mocker,
    blueprint_path: str,
) -> None:
    graphql_responses(requests_mock, upload_payload(UPLOAD_URL))
    requests_mock.post(
        UPLOAD_PROXY_URL, status_code=302, headers={"Location": "mock://other/up"}
    )
    other = requests_mock.post("mock://other/up", json=RAINBOW_LIST)

    with pytest.raises(IndicoRequestError, match="302"):
        client.call(UploadFieldBlueprints(file_path=blueprint_path))
    assert other.call_count == 0


@pytest.mark.parametrize(
    "status, result, error",
    [
        ("SUCCESS", {"count": 1}, None),
        ("FAILURE", {"message": "bad blueprint file"}, "bad blueprint file"),
        ("FAILURE", {"detail": "unknown shape"}, "Failed to import field blueprints"),
        ("FAILURE", None, "Failed to import field blueprints"),
    ],
)
def test_upload_auto_import(
    client: IndicoClient,
    requests_mock: requests_mock_lib.Mocker,
    blueprint_path: str,
    status: str,
    result: Any,
    error: Optional[str],
) -> None:
    job = job_payload(status, result)
    responses = [
        upload_payload(UPLOAD_URL),
        {"data": {"importFieldBlueprints": {"jobId": "j1"}}},
        job,
        job,
    ]
    graphql = graphql_responses(requests_mock, *responses)
    requests_mock.post(UPLOAD_PROXY_URL, json=RAINBOW_LIST, headers=JSON_HEADERS)
    chain = UploadFieldBlueprints(file_path=blueprint_path, auto_import=True)

    if error:
        with pytest.raises(IndicoRequestError, match=error):
            client.call(chain)
    else:
        imported = client.call(chain)
        assert isinstance(imported, Job)
        assert (imported.status, imported.result) == ("SUCCESS", result)

    assert graphql.call_count == len(responses)
    assert graphql.request_history[1].json()["variables"] == {"storageUri": STORAGE_URI}
    assert len(transfers(requests_mock, UPLOAD_PATH)) == 1


def test_upload_auto_import_without_wait(
    client: IndicoClient,
    requests_mock: requests_mock_lib.Mocker,
    blueprint_path: str,
) -> None:
    graphql = graphql_responses(
        requests_mock,
        upload_payload(UPLOAD_URL),
        {"data": {"importFieldBlueprints": {"jobId": "j1"}}},
    )
    requests_mock.post(UPLOAD_PROXY_URL, json=RAINBOW_LIST, headers=JSON_HEADERS)

    job = client.call(
        UploadFieldBlueprints(file_path=blueprint_path, auto_import=True, wait=False)
    )

    assert isinstance(job, Job)
    assert str(job.id) == "j1"
    assert graphql.call_count == 2


def test_export_then_download(
    client: IndicoClient, requests_mock: requests_mock_lib.Mocker
) -> None:
    job = job_payload("SUCCESS", EXPORT_RESULT)
    graphql_responses(
        requests_mock,
        {"data": {"exportFieldBlueprints": {"jobId": "j1"}}},
        job,
        job,
    )
    download = requests_mock.get(
        DOWNLOAD_PROXY_URL,
        content=json.dumps(EXPORT_BODY).encode(),
        headers=OCTET_HEADERS,
    )

    export_job = client.call(ExportFieldBlueprints(field_blueprint_ids=[1]))

    assert client.call(DownloadFieldBlueprintExport(export_job)) == EXPORT_BODY
    assert "auth_token=tok" in download.request_history[-1].headers["Cookie"]


def test_download_does_not_follow_redirects(
    client: IndicoClient, requests_mock: requests_mock_lib.Mocker
) -> None:
    requests_mock.get(
        DOWNLOAD_PROXY_URL, status_code=302, headers={"Location": "mock://other/x"}
    )
    other = requests_mock.get("mock://other/x", json=EXPORT_BODY)

    with pytest.raises(IndicoRequestError, match="302"):
        client.call(
            DownloadFieldBlueprintExport(finished_job("SUCCESS", EXPORT_RESULT))
        )
    assert other.call_count == 0


@pytest.mark.parametrize(
    "job, error, match",
    [
        (finished_job("FAILURE", EXPORT_RESULT), IndicoRequestError, "SUCCESS"),
        (finished_job("PENDING", None), IndicoRequestError, "SUCCESS"),
        (Job(id="j1"), IndicoRequestError, "SUCCESS"),
        (finished_job("SUCCESS", None), IndicoInputError, "download_url"),
        (finished_job("SUCCESS", {"count": 0}), IndicoInputError, "download_url"),
        (finished_job("SUCCESS", "done"), IndicoInputError, "download_url"),
        (
            finished_job("SUCCESS", {"download_url": f"https://h{DOWNLOAD_URL}"}),
            IndicoRequestError,
            "Unexpected storage URL",
        ),
    ],
)
def test_download_rejects(
    client: IndicoClient,
    requests_mock: requests_mock_lib.Mocker,
    job: Job,
    error: type,
    match: str,
) -> None:
    with pytest.raises(error, match=match):
        client.call(DownloadFieldBlueprintExport(job))
    assert [r for r in requests_mock.request_history if r.method == "GET"] == []


@pytest.mark.asyncio
async def test_upload_proxied_async(
    aio_client: AsyncIndicoClient,
    fake_aio_session: FakeAioSession,
    blueprint_path: str,
) -> None:
    fake_aio_session.responses.extend(
        [
            FakeAioResponse(
                body=json.dumps(upload_payload(UPLOAD_URL)).encode(),
                headers=JSON_HEADERS,
            ),
            FakeAioResponse(
                body=json.dumps(RAINBOW_LIST).encode(), headers=JSON_HEADERS
            ),
        ]
    )

    result = await aio_client.call(UploadFieldBlueprints(file_path=blueprint_path))

    assert result == STORAGE_URI
    upload = fake_aio_session.calls[-1]
    assert (upload.method, upload.url) == ("post", f"{UPLOAD_PROXY_URL}?name={NAME}")
    assert upload.kwargs["allow_redirects"] is False
    assert upload.kwargs["timeout"] is None
    assert upload.body is not None
    assert b'filename="blueprints.json"' in upload.body


@pytest.mark.asyncio
async def test_download_async(
    aio_client: AsyncIndicoClient, fake_aio_session: FakeAioSession
) -> None:
    fake_aio_session.responses.append(
        FakeAioResponse(body=json.dumps(EXPORT_BODY).encode(), headers=OCTET_HEADERS)
    )

    result = await aio_client.call(
        DownloadFieldBlueprintExport(finished_job("SUCCESS", EXPORT_RESULT))
    )

    assert result == EXPORT_BODY
    download = fake_aio_session.calls[-1]
    assert (download.method, download.url) == ("get", DOWNLOAD_PROXY_URL)
    assert download.kwargs["allow_redirects"] is False
    assert download.kwargs["timeout"] is None


@pytest.mark.asyncio
async def test_download_async_does_not_follow_redirects(
    aio_client: AsyncIndicoClient, fake_aio_session: FakeAioSession
) -> None:
    fake_aio_session.responses.extend(
        [
            FakeAioResponse(status=302, headers={"Location": "mock://other/x"}),
            FakeAioResponse(body=json.dumps(EXPORT_BODY).encode()),
        ]
    )

    with pytest.raises(IndicoRequestError, match="302"):
        await aio_client.call(
            DownloadFieldBlueprintExport(finished_job("SUCCESS", EXPORT_RESULT))
        )
    assert "mock://other/x" not in [call.url for call in fake_aio_session.calls]


HTML_413 = b"<html><body>413 Request Entity Too Large</body></html>"


def test_upload_html_413_is_request_error(
    client: IndicoClient,
    requests_mock: requests_mock_lib.Mocker,
    blueprint_path: str,
) -> None:
    graphql_responses(requests_mock, upload_payload(UPLOAD_URL))
    requests_mock.post(
        UPLOAD_PROXY_URL, status_code=413, content=HTML_413, headers=HTML_HEADERS
    )

    with pytest.raises(IndicoRequestError, match="Status: 413"):
        client.call(UploadFieldBlueprints(file_path=blueprint_path))


@pytest.mark.asyncio
async def test_upload_html_413_is_request_error_async(
    aio_client: AsyncIndicoClient,
    fake_aio_session: FakeAioSession,
    blueprint_path: str,
) -> None:
    fake_aio_session.responses.extend(
        [
            FakeAioResponse(
                body=json.dumps(upload_payload(UPLOAD_URL)).encode(),
                headers=JSON_HEADERS,
            ),
            FakeAioResponse(status=413, body=HTML_413, headers=HTML_HEADERS),
        ]
    )

    with pytest.raises(IndicoRequestError, match="Status: 413"):
        await aio_client.call(UploadFieldBlueprints(file_path=blueprint_path))


@pytest.mark.asyncio
async def test_upload_auto_import_async(
    aio_client: AsyncIndicoClient,
    fake_aio_session: FakeAioSession,
    blueprint_path: str,
) -> None:
    bodies = [
        upload_payload(UPLOAD_URL),
        RAINBOW_LIST,
        {"data": {"importFieldBlueprints": {"jobId": "j1"}}},
        job_payload("SUCCESS", {"count": 1}),
        job_payload("SUCCESS", {"count": 1}),
    ]
    fake_aio_session.responses.extend(
        FakeAioResponse(body=json.dumps(body).encode(), headers=JSON_HEADERS)
        for body in bodies
    )

    job = await aio_client.call(
        UploadFieldBlueprints(file_path=blueprint_path, auto_import=True)
    )

    assert isinstance(job, Job)
    assert job.status == "SUCCESS"
    assert fake_aio_session.calls[-3].kwargs["json"]["variables"] == {
        "storageUri": STORAGE_URI
    }


@pytest.mark.parametrize(
    "result, message",
    [
        ({"detail": "x"}, "Error: Failed to import field blueprints"),
        ({"message": "bad"}, "Error: Failed to import field blueprints: bad"),
    ],
)
def test_upload_failure_message_has_no_none_tail(
    client: IndicoClient,
    requests_mock: requests_mock_lib.Mocker,
    blueprint_path: str,
    result: Any,
    message: str,
) -> None:
    job = job_payload("FAILURE", result)
    graphql_responses(
        requests_mock,
        upload_payload(UPLOAD_URL),
        {"data": {"importFieldBlueprints": {"jobId": "j1"}}},
        job,
        job,
    )
    requests_mock.post(UPLOAD_PROXY_URL, json=RAINBOW_LIST, headers=JSON_HEADERS)

    with pytest.raises(IndicoRequestError) as raised:
        client.call(UploadFieldBlueprints(file_path=blueprint_path, auto_import=True))
    assert str(raised.value).split("\n")[0].endswith(message)
