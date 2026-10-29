import json
from pathlib import Path
from typing import Any, Dict, List, Optional

import aiohttp
import pytest
import requests_mock as requests_mock_lib

from indico.client import AsyncIndicoClient, IndicoClient
from indico.errors import IndicoAuthenticationFailed, IndicoRequestError
from indico.queries.model_import import UploadStaticModelExport
from tests.fixtures.transport import FakeAioResponse, FakeAioSession, RequestMocker

NAME = "3f8a1c2e-4b5d-6e7f-8a9b-0c1d2e3f4a5b.indico"
UPLOAD_URL = f"/storage/static_uploads/upload?name={NAME}"
STORAGE_URI = f"indico-blob:///static_uploads/{NAME}"
PROXY_PATH = "/storage/static_uploads/upload"
PROXY_URL = f"mock://mock{PROXY_PATH}"
JSON_HEADERS = {"Content-Type": "application/json"}
RAINBOW_LIST = [
    {
        "path": "/static_uploads/x.indico",
        "name": "m.indico",
        "size": 3,
        "upload_type": "user",
    }
]


def export_upload_payload(upload_url: Optional[str]) -> Dict[str, Any]:
    return {
        "data": {"exportUpload": {"uploadUrl": upload_url, "storageUri": STORAGE_URI}}
    }


def job_payload(status: str, result: str) -> Dict[str, Any]:
    return {
        "data": {"job": {"id": "j1", "ready": True, "status": status, "result": result}}
    }


@pytest.fixture
def zip_path(tmp_path: Path) -> str:
    path = tmp_path / "model.zip"
    path.write_bytes(b"zip-bytes")
    return str(path)


def test_upload_proxied(
    indico_request: RequestMocker,
    client: IndicoClient,
    requests_mock: requests_mock_lib.Mocker,
    zip_path: str,
) -> None:
    indico_request("post", "/graph/api/graphql", json=export_upload_payload(UPLOAD_URL))
    proxy = requests_mock.post(
        PROXY_URL, json=RAINBOW_LIST, headers={"Content-Type": "application/json"}
    )

    assert client.call(UploadStaticModelExport(file_path=zip_path)) == STORAGE_URI
    assert "auth_token=tok" in proxy.last_request.headers["Cookie"]
    assert proxy.last_request.qs == {"name": [NAME]}
    assert b"zip-bytes" in proxy.last_request.body


def test_upload_resent_after_auth_refresh(
    indico_request: RequestMocker,
    client: IndicoClient,
    requests_mock: requests_mock_lib.Mocker,
    zip_path: str,
) -> None:
    indico_request("post", "/graph/api/graphql", json=export_upload_payload(UPLOAD_URL))
    proxy = requests_mock.post(
        PROXY_URL,
        [
            {"status_code": 401, "json": {}, "headers": JSON_HEADERS},
            {"json": RAINBOW_LIST, "headers": JSON_HEADERS},
        ],
    )

    assert client.call(UploadStaticModelExport(file_path=zip_path)) == STORAGE_URI
    assert [b"zip-bytes" in r.body for r in proxy.request_history] == [True, True]


@pytest.mark.parametrize(
    "job_status, result, error",
    [
        ("SUCCESS", "{}", None),
        ("FAILURE", '{"message": "bad export"}', "bad export"),
    ],
)
def test_upload_auto_process(
    client: IndicoClient,
    requests_mock: requests_mock_lib.Mocker,
    zip_path: str,
    job_status: str,
    result: str,
    error: Optional[str],
) -> None:
    job = job_payload(job_status, result)
    responses = [
        export_upload_payload(UPLOAD_URL),
        {"data": {"processStaticModelExport": {"jobId": "j1"}}},
        job,
        job,
    ]
    graphql = requests_mock.post(
        "mock://mock/graph/api/graphql",
        [{"json": body, "headers": JSON_HEADERS} for body in responses],
    )
    requests_mock.post(PROXY_URL, json=RAINBOW_LIST, headers=JSON_HEADERS)
    chain = UploadStaticModelExport(
        file_path=zip_path, auto_process=True, workflow_id=1
    )

    if error:
        with pytest.raises(IndicoRequestError, match=error):
            client.call(chain)
    else:
        client.call(chain)

    assert graphql.call_count == len(responses)
    assert graphql.request_history[1].json()["variables"] == {
        "storageUri": STORAGE_URI,
        "workflowId": 1,
    }


@pytest.mark.parametrize(
    "upload_url, proxy_status",
    [
        (UPLOAD_URL, 413),
        ("https://h/storage/static_uploads/upload?name=x", None),
    ],
)
def test_upload_failures(
    indico_request: RequestMocker,
    client: IndicoClient,
    requests_mock: requests_mock_lib.Mocker,
    zip_path: str,
    upload_url: Optional[str],
    proxy_status: Optional[int],
) -> None:
    graphql = indico_request(
        "post", "/graph/api/graphql", json=export_upload_payload(upload_url)
    )
    if proxy_status:
        requests_mock.post(
            PROXY_URL,
            status_code=proxy_status,
            text="too large",
            headers={"Content-Type": "text/plain"},
        )

    with pytest.raises(IndicoRequestError):
        client.call(
            UploadStaticModelExport(
                file_path=zip_path, auto_process=True, workflow_id=1
            )
        )
    assert graphql.call_count == 1
    transfers = [r for r in requests_mock.request_history if r.path == PROXY_PATH]
    assert len(transfers) == int(bool(proxy_status))


def test_upload_does_not_follow_redirects(
    indico_request: RequestMocker,
    client: IndicoClient,
    requests_mock: requests_mock_lib.Mocker,
    zip_path: str,
) -> None:
    indico_request("post", "/graph/api/graphql", json=export_upload_payload(UPLOAD_URL))
    requests_mock.post(
        PROXY_URL, status_code=302, headers={"Location": "mock://other/upload"}
    )
    other = requests_mock.post("mock://other/upload", json=RAINBOW_LIST)
    with pytest.raises(IndicoRequestError, match="302"):
        client.call(UploadStaticModelExport(file_path=zip_path))
    assert other.call_count == 0


def upload_exchange(*upload_responses: FakeAioResponse) -> List[FakeAioResponse]:
    return [
        FakeAioResponse(
            body=json.dumps(export_upload_payload(UPLOAD_URL)).encode(),
            headers=JSON_HEADERS,
        ),
        *upload_responses,
    ]


RAINBOW_OK = FakeAioResponse(
    body=json.dumps(RAINBOW_LIST).encode(), headers=JSON_HEADERS
)


@pytest.mark.asyncio
async def test_upload_proxied_async(
    aio_client: AsyncIndicoClient, fake_aio_session: FakeAioSession, zip_path: str
) -> None:
    fake_aio_session.responses.extend(upload_exchange(RAINBOW_OK))

    result = await aio_client.call(UploadStaticModelExport(file_path=zip_path))

    assert result == STORAGE_URI
    upload = fake_aio_session.calls[-1]
    assert (upload.method, upload.url, upload.kwargs["allow_redirects"]) == (
        "post",
        f"{PROXY_URL}?name={NAME}",
        False,
    )
    assert upload.kwargs["timeout"] == aiohttp.ClientTimeout(total=None)
    assert upload.body is not None
    assert b'filename="model.zip"' in upload.body
    assert b"zip-bytes" in upload.body


@pytest.mark.asyncio
async def test_upload_async_resent_after_auth_refresh(
    aio_client: AsyncIndicoClient, fake_aio_session: FakeAioSession, zip_path: str
) -> None:
    fake_aio_session.responses.extend(
        upload_exchange(
            FakeAioResponse(status=401),
            FakeAioResponse(body=b'{"auth_token": "t2"}', headers=JSON_HEADERS),
            RAINBOW_OK,
        )
    )

    result = await aio_client.call(UploadStaticModelExport(file_path=zip_path))

    assert result == STORAGE_URI
    uploads = [call for call in fake_aio_session.calls if PROXY_PATH in call.url]
    assert [b"zip-bytes" in (call.body or b"") for call in uploads] == [True, True]


@pytest.mark.asyncio
async def test_upload_async_auth_failure_after_refresh(
    aio_client: AsyncIndicoClient, fake_aio_session: FakeAioSession, zip_path: str
) -> None:
    fake_aio_session.responses.extend(
        upload_exchange(
            FakeAioResponse(status=401),
            FakeAioResponse(body=b'{"auth_token": "t2"}', headers=JSON_HEADERS),
            FakeAioResponse(status=401),
        )
    )

    with pytest.raises(IndicoAuthenticationFailed):
        await aio_client.call(UploadStaticModelExport(file_path=zip_path))
    assert fake_aio_session.responses == []


@pytest.mark.asyncio
async def test_upload_async_does_not_follow_redirects(
    aio_client: AsyncIndicoClient, fake_aio_session: FakeAioSession, zip_path: str
) -> None:
    fake_aio_session.responses.extend(
        upload_exchange(
            FakeAioResponse(status=302, headers={"Location": "mock://other/upload"}),
            RAINBOW_OK,
        )
    )

    with pytest.raises(IndicoRequestError, match="302"):
        await aio_client.call(UploadStaticModelExport(file_path=zip_path))
    assert "mock://other/upload" not in [call.url for call in fake_aio_session.calls]
