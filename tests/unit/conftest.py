from typing import Any, AsyncIterator

import pytest
import pytest_asyncio
import requests_mock as requests_mock_lib

from indico.client import AsyncIndicoClient, IndicoClient
from indico.config import IndicoConfig
from indico.http.client import AIOHTTPClient
from tests.fixtures.transport import FakeAioResponse, FakeAioSession, RequestMocker

JSON_HEADERS = {"Content-Type": "application/json"}


@pytest.fixture(scope="function")
def indico_test_config() -> IndicoConfig:
    return IndicoConfig(protocol="mock", host="mock", api_token="test")


@pytest.fixture(scope="function")
def indico_request(
    requests_mock: requests_mock_lib.Mocker, indico_test_config: IndicoConfig
) -> RequestMocker:
    def new_request_mock(method: str, path: str, *args: Any, **kwargs: Any) -> Any:
        config = indico_test_config
        url = f"{config.protocol}://{config.host}" + path
        return getattr(requests_mock, method)(
            url, *args, **kwargs, headers={"Content-Type": "application/json"}
        )

    return new_request_mock


@pytest.fixture(scope="function")
def auth(indico_request: RequestMocker) -> None:
    indico_request(
        "post",
        "/auth/users/refresh_token",
        json={"auth_token": "asdfsdfasdfasdfasdfasdf"},
    )


@pytest.fixture(scope="function")
def client(auth: None, indico_test_config: IndicoConfig) -> IndicoClient:
    indico_client = IndicoClient(config=indico_test_config)
    indico_client._http.request_session.cookies.set("auth_token", "tok")
    return indico_client


@pytest.fixture(scope="function")
def fake_aio_session() -> FakeAioSession:
    return FakeAioSession()


@pytest_asyncio.fixture(scope="function")
async def aio_http(
    indico_test_config: IndicoConfig,
    fake_aio_session: FakeAioSession,
    monkeypatch: pytest.MonkeyPatch,
) -> AsyncIterator[AIOHTTPClient]:
    http = AIOHTTPClient(config=indico_test_config)
    await http.request_session.close()
    monkeypatch.setattr(http, "request_session", fake_aio_session)
    yield http


@pytest_asyncio.fixture(scope="function")
async def aio_client(
    indico_test_config: IndicoConfig,
    fake_aio_session: FakeAioSession,
    monkeypatch: pytest.MonkeyPatch,
) -> AsyncIterator[AsyncIndicoClient]:
    indico_client = AsyncIndicoClient(config=indico_test_config)
    await indico_client._http.request_session.close()
    monkeypatch.setattr(indico_client._http, "request_session", fake_aio_session)
    fake_aio_session.responses.append(
        FakeAioResponse(body=b'{"auth_token": "t"}', headers=JSON_HEADERS)
    )
    yield await indico_client.create()
