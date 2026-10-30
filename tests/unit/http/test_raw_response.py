import io
from typing import Any, Dict

import pytest
import requests_mock as requests_mock_lib

from indico.client import HTTPMethod, HTTPRequest, IndicoClient
from indico.errors import IndicoDecodingError, IndicoRequestError
from indico.http.client import AIOHTTPClient
from tests.fixtures.transport import FakeAioResponse, FakeAioSession

BODY = b"\xff\xfezip"
PATH = "/storage/x"
URL = f"mock://mock{PATH}"
OTHER_URL = "mock://other/storage/x"
TEXT = {"Content-Type": "text/plain"}
JSON = {"Content-Type": "application/json"}
OCTET = {"Content-Type": "application/octet-stream"}
REDIRECT = {"Location": OTHER_URL, "Content-Type": "text/plain"}
JSON_ERROR = b'{"error_type": "NotFound", "message": "missing", "detail": 1}'

ERROR_CASES = [
    pytest.param(
        JSON_ERROR, JSON, "Error: NotFound, missing\n\tExtras: {'detail': 1}", id="json"
    ),
    pytest.param(b"bad\xff", OCTET, "Error: b'bad\\xff'\n", id="bytes"),
]


def raw_get(**kwargs: Any) -> HTTPRequest[Any]:
    return HTTPRequest[Any](HTTPMethod.GET, PATH, raw_response=True, **kwargs)


def test_raw_returns_bytes(
    client: IndicoClient, requests_mock: requests_mock_lib.Mocker
) -> None:
    requests_mock.get(URL, content=BODY, headers=TEXT)
    assert client.call(raw_get()) == BODY


def test_non_raw_decoding_error(
    client: IndicoClient, requests_mock: requests_mock_lib.Mocker
) -> None:
    requests_mock.get(URL, content=BODY, headers=TEXT)
    with pytest.raises(IndicoDecodingError):
        client.call(HTTPRequest[Any](HTTPMethod.GET, PATH))


def test_raw_survives_auth_refresh(
    client: IndicoClient, requests_mock: requests_mock_lib.Mocker
) -> None:
    requests_mock.get(
        URL,
        [
            {"status_code": 401, "json": {}, "headers": JSON},
            {"content": BODY, "headers": TEXT},
        ],
    )
    assert client.call(raw_get()) == BODY


def test_redirect_is_not_followed(
    client: IndicoClient, requests_mock: requests_mock_lib.Mocker
) -> None:
    requests_mock.get(URL, status_code=302, headers=REDIRECT)
    other = requests_mock.get(OTHER_URL, content=BODY, headers=TEXT)
    with pytest.raises(IndicoRequestError, match="302"):
        client.call(raw_get(allow_redirects=False))
    assert other.call_count == 0


def test_unfollowable_redirect_without_opt_out_is_returned(
    client: IndicoClient, requests_mock: requests_mock_lib.Mocker
) -> None:
    requests_mock.get(URL, status_code=304, json={"cached": True}, headers=JSON)
    assert client.call(HTTPRequest[Any](HTTPMethod.GET, PATH)) == {"cached": True}


@pytest.mark.parametrize("body, headers, expected", ERROR_CASES)
def test_client_error_body(
    client: IndicoClient,
    requests_mock: requests_mock_lib.Mocker,
    body: bytes,
    headers: Dict[str, str],
    expected: str,
) -> None:
    requests_mock.get(URL, status_code=404, content=body, headers=headers)
    with pytest.raises(IndicoRequestError) as error:
        client.call(raw_get())
    assert expected in str(error.value)


@pytest.mark.asyncio
async def test_async_raw_returns_bytes(
    aio_http: AIOHTTPClient, fake_aio_session: FakeAioSession
) -> None:
    fake_aio_session.responses.append(FakeAioResponse(body=BODY))
    assert await aio_http.execute_request(raw_get()) == BODY


@pytest.mark.asyncio
async def test_async_non_raw_decoding_error(
    aio_http: AIOHTTPClient, fake_aio_session: FakeAioSession
) -> None:
    fake_aio_session.responses.append(FakeAioResponse(body=BODY))
    with pytest.raises(IndicoDecodingError):
        await aio_http.execute_request(HTTPRequest[Any](HTTPMethod.GET, PATH))


@pytest.mark.asyncio
async def test_async_raw_survives_auth_refresh(
    aio_http: AIOHTTPClient, fake_aio_session: FakeAioSession
) -> None:
    fake_aio_session.responses.extend(
        [
            FakeAioResponse(status=401),
            FakeAioResponse(body=b'{"auth_token": "t"}', headers=JSON),
            FakeAioResponse(body=BODY),
        ]
    )
    assert await aio_http.execute_request(raw_get()) == BODY
    assert [call.method for call in fake_aio_session.calls] == ["get", "post", "get"]


@pytest.mark.asyncio
async def test_async_stream_upload_is_not_resent_after_auth_refresh(
    aio_http: AIOHTTPClient, fake_aio_session: FakeAioSession
) -> None:
    fake_aio_session.responses.extend(
        [FakeAioResponse(status=401), FakeAioResponse(body=BODY)]
    )
    request = HTTPRequest[Any](
        HTTPMethod.POST, PATH, streams={"model.zip": io.BytesIO(b"zip")}
    )
    with pytest.raises(IndicoRequestError, match="cannot be resent"):
        await aio_http.execute_request(request)
    assert len(fake_aio_session.calls) == 1


@pytest.mark.asyncio
async def test_async_redirect_is_not_followed(
    aio_http: AIOHTTPClient, fake_aio_session: FakeAioSession
) -> None:
    fake_aio_session.responses.extend(
        [FakeAioResponse(status=302, headers=REDIRECT), FakeAioResponse(body=BODY)]
    )
    with pytest.raises(IndicoRequestError, match="302"):
        await aio_http.execute_request(raw_get(allow_redirects=False))
    assert [call.url for call in fake_aio_session.calls] == [URL]


@pytest.mark.asyncio
@pytest.mark.parametrize("body, headers, expected", ERROR_CASES)
async def test_async_client_error_body(
    aio_http: AIOHTTPClient,
    fake_aio_session: FakeAioSession,
    body: bytes,
    headers: Dict[str, str],
    expected: str,
) -> None:
    fake_aio_session.responses.append(
        FakeAioResponse(status=404, body=body, headers=headers)
    )
    with pytest.raises(IndicoRequestError) as error:
        await aio_http.execute_request(raw_get())
    assert expected in str(error.value)
