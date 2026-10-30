import inspect
import json
import warnings
from typing import Any, Dict, Optional

import pytest
import requests_mock as requests_mock_lib

from indico.client import AsyncIndicoClient, IndicoClient
from indico.errors import IndicoInputError, IndicoRequestError
from indico.queries.model_export import (
    CreateModelExport,
    DownloadModelExport,
    GetModelExports,
)
from indico.types.model_export import ModelExport
from tests.fixtures.transport import FakeAioResponse, FakeAioSession, RequestMocker

DOWNLOAD_URL = "/storage/models/exports/7/model.zip"
DOWNLOAD_PROXY_URL = f"mock://mock{DOWNLOAD_URL}"
GRAPHQL_URL = "mock://mock/graph/api/graphql"
JSON = {"Content-Type": "application/json"}
BODY = b"\xff\xfezip"


def export_record(status: str, download_url: Optional[str]) -> Dict[str, Any]:
    return {
        "id": 7,
        "name": "m",
        "status": status,
        "modelId": 1,
        "filePath": "/p",
        "createdAt": "2026-01-01T00:00:00",
        "createdBy": 2,
        "downloadUrl": download_url,
    }


def exports_payload(*exports: Dict[str, Any]) -> Dict[str, Any]:
    return {"data": {"modelExports": {"modelExports": list(exports)}}}


def export_payload(status: str, download_url: Optional[str]) -> Dict[str, Any]:
    return exports_payload(export_record(status, download_url))


def graphql_responses(
    requests_mock: requests_mock_lib.Mocker, *bodies: Dict[str, Any]
) -> Any:
    return requests_mock.post(
        GRAPHQL_URL, [{"json": body, "headers": JSON} for body in bodies]
    )


@pytest.mark.parametrize(
    "kwargs",
    [{"with_download_url": True}, {"with_signed_url": True}],
)
@pytest.mark.filterwarnings("ignore::DeprecationWarning")
def test_get_model_exports_selects_download_url(kwargs: Dict[str, bool]) -> None:
    query = GetModelExports([1], **kwargs).query
    assert "downloadUrl" in query
    assert "signedUrl" not in query


def test_get_model_exports_omits_urls_by_default() -> None:
    query = GetModelExports([1]).query
    assert "downloadUrl" not in query
    assert "signedUrl" not in query


def test_get_model_exports_fields_do_not_accumulate() -> None:
    GetModelExports([1], with_download_url=True)
    assert "downloadUrl" not in GetModelExports([1]).query


def test_with_signed_url_is_deprecated() -> None:
    with pytest.warns(DeprecationWarning, match="with_download_url") as record:
        caller_line = inspect.stack(0)[0].lineno + 1
        GetModelExports([1], with_signed_url=True)
    assert record[0].category is DeprecationWarning
    assert record[0].lineno == caller_line


def test_with_signed_url_populates_download_url(
    indico_request: RequestMocker, client: IndicoClient
) -> None:
    indico_request(
        "post", "/graph/api/graphql", json=export_payload("COMPLETE", DOWNLOAD_URL)
    )
    with pytest.warns(DeprecationWarning):
        request = GetModelExports([7], with_signed_url=True)
    [export] = client.call(request)
    assert export.download_url == DOWNLOAD_URL
    assert export.signed_url is None


def test_signed_url_is_ignored_when_returned() -> None:
    record = {**export_record("COMPLETE", DOWNLOAD_URL), "signedUrl": "https://x"}
    assert ModelExport(**record).signed_url is None


def test_get_model_exports_download_url(
    indico_request: RequestMocker, client: IndicoClient
) -> None:
    indico_request(
        "post", "/graph/api/graphql", json=export_payload("COMPLETE", DOWNLOAD_URL)
    )
    [export] = client.call(GetModelExports([7], with_download_url=True))
    assert export.download_url == DOWNLOAD_URL


@pytest.mark.parametrize("wait", [True, False])
def test_create_model_export_final_fetch_fields(
    client: IndicoClient, requests_mock: requests_mock_lib.Mocker, wait: bool
) -> None:
    created = {"id": 7, "name": "m", "status": "COMPLETE", "modelId": 1}
    graphql = graphql_responses(
        requests_mock,
        {"data": {"createModelExport": created}},
        export_payload("COMPLETE", DOWNLOAD_URL),
    )
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        client.call(CreateModelExport(model_id=1, wait=wait))
    query = graphql.last_request.json()["query"]
    assert ("downloadUrl" in query) is wait
    assert "signedUrl" not in query


def test_create_then_download_model_export(
    client: IndicoClient, requests_mock: requests_mock_lib.Mocker
) -> None:
    created = {"id": 7, "name": "m", "status": "COMPLETE", "modelId": 1}
    graphql_responses(
        requests_mock,
        {"data": {"createModelExport": created}},
        export_payload("COMPLETE", DOWNLOAD_URL),
    )
    requests_mock.get(DOWNLOAD_PROXY_URL, content=BODY, headers=JSON)
    [export] = client.call(CreateModelExport(model_id=1))
    assert client.call(DownloadModelExport(export=export)) == BODY


@pytest.mark.parametrize("content_type", ["application/zip", "text/plain"])
@pytest.mark.parametrize("by_id", [True, False])
def test_download_model_export(
    indico_request: RequestMocker,
    client: IndicoClient,
    requests_mock: requests_mock_lib.Mocker,
    content_type: str,
    by_id: bool,
) -> None:
    graphql = indico_request(
        "post", "/graph/api/graphql", json=export_payload("COMPLETE", DOWNLOAD_URL)
    )
    download = requests_mock.get(
        DOWNLOAD_PROXY_URL, content=BODY, headers={"Content-Type": content_type}
    )
    if by_id:
        chain = DownloadModelExport(export_id=7)
    else:
        chain = DownloadModelExport(
            export=ModelExport(**export_record("COMPLETE", DOWNLOAD_URL))
        )

    assert client.call(chain) == BODY
    assert graphql.call_count == int(by_id)
    assert "auth_token=tok" in download.last_request.headers["Cookie"]


def test_download_model_export_id_zero_is_fetched(
    indico_request: RequestMocker,
    client: IndicoClient,
    requests_mock: requests_mock_lib.Mocker,
) -> None:
    graphql = indico_request(
        "post", "/graph/api/graphql", json=export_payload("COMPLETE", DOWNLOAD_URL)
    )
    requests_mock.get(DOWNLOAD_PROXY_URL, content=BODY, headers=JSON)
    assert client.call(DownloadModelExport(export_id=0)) == BODY
    assert graphql.last_request.json()["variables"] == {"exportIds": [0]}


def test_download_model_export_does_not_follow_redirects(
    indico_request: RequestMocker,
    client: IndicoClient,
    requests_mock: requests_mock_lib.Mocker,
) -> None:
    indico_request(
        "post", "/graph/api/graphql", json=export_payload("COMPLETE", DOWNLOAD_URL)
    )
    requests_mock.get(
        DOWNLOAD_PROXY_URL,
        status_code=302,
        headers={"Location": "mock://other/exports/model.zip"},
    )
    other = requests_mock.get("mock://other/exports/model.zip", content=BODY)
    with pytest.raises(IndicoRequestError, match="302"):
        client.call(DownloadModelExport(export_id=7))
    assert other.call_count == 0


@pytest.mark.asyncio
async def test_download_model_export_async_does_not_follow_redirects(
    aio_client: AsyncIndicoClient, fake_aio_session: FakeAioSession
) -> None:
    fake_aio_session.responses.extend(
        [
            FakeAioResponse(
                body=json.dumps(export_payload("COMPLETE", DOWNLOAD_URL)).encode(),
                headers=JSON,
            ),
            FakeAioResponse(status=302, headers={"Location": "mock://other/x"}),
            FakeAioResponse(body=BODY),
        ]
    )
    with pytest.raises(IndicoRequestError, match="302"):
        await aio_client.call(DownloadModelExport(export_id=7))
    assert fake_aio_session.calls[-1].url == DOWNLOAD_PROXY_URL
    assert fake_aio_session.calls[-1].kwargs["allow_redirects"] is False


@pytest.mark.parametrize(
    "payload, match",
    [
        (export_payload("EXPORTING", DOWNLOAD_URL), "must be complete"),
        (exports_payload(), "not found"),
    ],
)
def test_download_model_export_rejects(
    indico_request: RequestMocker,
    client: IndicoClient,
    payload: Dict[str, Any],
    match: str,
) -> None:
    indico_request("post", "/graph/api/graphql", json=payload)
    with pytest.raises(IndicoRequestError, match=match):
        client.call(DownloadModelExport(export_id=7))


@pytest.mark.parametrize(
    "export",
    [
        ModelExport(id=1, status="COMPLETE"),
        ModelExport(**export_record("COMPLETE", None)),
    ],
)
def test_download_model_export_needs_download_url(
    client: IndicoClient, export: ModelExport
) -> None:
    with pytest.raises(IndicoInputError, match="with_download_url=True"):
        client.call(DownloadModelExport(export=export))


@pytest.mark.parametrize(
    "kwargs",
    [
        {},
        {"export_id": None, "export": None},
        {"export_id": 7, "export": ModelExport(**export_record("COMPLETE", None))},
    ],
)
def test_download_model_export_needs_exactly_one_source(
    kwargs: Dict[str, Any],
) -> None:
    with pytest.raises(IndicoInputError, match="exactly one"):
        DownloadModelExport(**kwargs)
