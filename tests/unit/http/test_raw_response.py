import io
from pathlib import Path
from typing import Any, Dict

import pytest
import requests_mock as requests_mock_lib

from indico.client import HTTPMethod, HTTPRequest, IndicoClient
from indico.config import IndicoConfig
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
MOCK_CONFIG = IndicoConfig(protocol="mock", host="mock", api_token="test")
SECURE_CONFIG = IndicoConfig(protocol="https", host="app.test", api_token="test")
PORT_CONFIG = IndicoConfig(protocol="http", host="app.test:8080", api_token="test")
JSON_ERROR = b'{"error_type": "NotFound", "message": "missing", "detail": 1}'

ERROR_CASES = [
    pytest.param(
        True,
        JSON_ERROR,
        JSON,
        "Error: NotFound, missing\n\tExtras: {'detail': 1}",
        id="raw-json",
    ),
    pytest.param(True, b"bad\xff", OCTET, "Error: bad\ufffd\n", id="raw-text"),
    pytest.param(True, b'["x"]', JSON, 'Error: ["x"]\n', id="raw-json-list"),
    pytest.param(False, b"bad\xff", OCTET, "Error: b'bad\\xff'\n", id="non-raw-bytes"),
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


@pytest.mark.parametrize(
    "indico_test_config, url, sent",
    [
        (MOCK_CONFIG, URL, True),
        (MOCK_CONFIG, OTHER_URL, False),
        (MOCK_CONFIG, "mock://mock.other/storage/x", False),
        (SECURE_CONFIG, f"https://app.test{PATH}", True),
        (SECURE_CONFIG, f"https://app.test:443{PATH}", True),
        (SECURE_CONFIG, f"http://app.test{PATH}", False),
        (SECURE_CONFIG, f"http://app.test:443{PATH}", False),
        (SECURE_CONFIG, f"https://app.test:8443{PATH}", False),
        (PORT_CONFIG, f"http://app.test:8080{PATH}", True),
        (PORT_CONFIG, f"http://app.test{PATH}", False),
    ],
)
def test_auth_cookie_only_sent_to_configured_host(
    client: IndicoClient, requests_mock: requests_mock_lib.Mocker, url: str, sent: bool
) -> None:
    requests_mock.get(url, text="ok")
    client._http.request_session.get(url)
    cookie = requests_mock.last_request.headers.get("Cookie", "")
    assert ("auth_token=tok" in cookie) is sent


@pytest.mark.parametrize(
    "indico_test_config, location, sent",
    [
        (MOCK_CONFIG, OTHER_URL, False),
        (SECURE_CONFIG, "http://app.test/storage/y", False),
        (SECURE_CONFIG, "http://app.test:443/storage/y", False),
        (SECURE_CONFIG, "https://app.test:8443/storage/y", False),
        (SECURE_CONFIG, "https://app.test/storage/y", True),
    ],
)
def test_followed_redirect_auth_cookie(
    client: IndicoClient,
    requests_mock: requests_mock_lib.Mocker,
    indico_test_config: IndicoConfig,
    location: str,
    sent: bool,
) -> None:
    base = f"{indico_test_config.protocol}://{indico_test_config.host}"
    requests_mock.get(
        base + PATH, status_code=302, headers={"Location": location, **TEXT}
    )
    target = requests_mock.get(location, content=BODY, headers=TEXT)
    assert client.call(raw_get()) == BODY
    cookie = target.last_request.headers.get("Cookie", "")
    assert ("auth_token=tok" in cookie) is sent


@pytest.mark.parametrize("indico_test_config", [MOCK_CONFIG, SECURE_CONFIG])
def test_explicit_timeout_wins_over_read_timeout(
    client: IndicoClient,
    requests_mock: requests_mock_lib.Mocker,
    indico_test_config: IndicoConfig,
) -> None:
    base = f"{indico_test_config.protocol}://{indico_test_config.host}"
    requests_mock.get(base + PATH, content=BODY, headers=TEXT)
    assert client.call(raw_get(read_timeout=600, timeout=5)) == BODY
    assert requests_mock.last_request.timeout == 5


@pytest.mark.parametrize("raw_response, body, headers, expected", ERROR_CASES)
def test_client_error_body(
    client: IndicoClient,
    requests_mock: requests_mock_lib.Mocker,
    raw_response: bool,
    body: bytes,
    headers: Dict[str, str],
    expected: str,
) -> None:
    requests_mock.get(URL, status_code=404, content=body, headers=headers)
    with pytest.raises(IndicoRequestError) as error:
        client.call(HTTPRequest[Any](HTTPMethod.GET, PATH, raw_response=raw_response))
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
async def test_async_raw_forwarded_per_file(
    aio_http: AIOHTTPClient, fake_aio_session: FakeAioSession, tmp_path: Path
) -> None:
    upload = tmp_path / "model.zip"
    upload.write_bytes(b"zip")
    fake_aio_session.responses.append(FakeAioResponse(body=BODY))
    request = HTTPRequest[Any](
        HTTPMethod.POST, PATH, raw_response=True, files=[str(upload)]
    )
    assert await aio_http.execute_request(request) == [BODY]


@pytest.mark.asyncio
async def test_async_raw_file_upload_survives_auth_refresh(
    aio_http: AIOHTTPClient, fake_aio_session: FakeAioSession, tmp_path: Path
) -> None:
    upload = tmp_path / "model.zip"
    upload.write_bytes(b"zip")
    fake_aio_session.responses.extend(
        [
            FakeAioResponse(status=401),
            FakeAioResponse(body=b'{"auth_token": "t"}', headers=JSON),
            FakeAioResponse(body=BODY),
        ]
    )
    request = HTTPRequest[Any](
        HTTPMethod.POST, PATH, raw_response=True, files=[str(upload)]
    )
    assert await aio_http.execute_request(request) == [BODY]


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
async def test_async_explicit_timeout_wins_over_read_timeout(
    aio_http: AIOHTTPClient, fake_aio_session: FakeAioSession
) -> None:
    fake_aio_session.responses.append(FakeAioResponse(body=BODY))
    assert await aio_http.execute_request(raw_get(read_timeout=600, timeout=5)) == BODY
    assert fake_aio_session.calls[-1].kwargs["timeout"] == 5


@pytest.mark.asyncio
@pytest.mark.parametrize("raw_response, body, headers, expected", ERROR_CASES)
async def test_async_client_error_body(
    aio_http: AIOHTTPClient,
    fake_aio_session: FakeAioSession,
    raw_response: bool,
    body: bytes,
    headers: Dict[str, str],
    expected: str,
) -> None:
    fake_aio_session.responses.append(
        FakeAioResponse(status=404, body=body, headers=headers)
    )
    with pytest.raises(IndicoRequestError) as error:
        await aio_http.execute_request(
            HTTPRequest[Any](HTTPMethod.GET, PATH, raw_response=raw_response)
        )
    assert expected in str(error.value)
