import pytest


from indico.client import AsyncIndicoClient, HTTPRequest, HTTPMethod, GraphQLRequest
from indico.config import IndicoConfig
from indico.errors import IndicoError

pytestmark = pytest.mark.asyncio(scope="module")


@pytest.fixture(scope="function")
def indico_test_config():
    return IndicoConfig(protocol="mock", host="mock")


@pytest.fixture(scope="function")
def indico_request(requests_mock, indico_test_config, monkeypatch):
    registered = {}

    async def _mock_make_request(self, method, path, *args, **kwargs):
        if (method, path) in registered:
            return registered[(method, path)]
        raise Exception(f"Unmocked {method} {path}")

    monkeypatch.setattr(
        "indico.http.client.AIOHTTPClient._make_request", _mock_make_request
    )

    def new_request_mock(method, path, json):
        registered[(method, path)] = json

    return new_request_mock


@pytest.fixture(scope="function")
def auth(indico_request):
    indico_request(
        "post",
        "/auth/users/refresh_token",
        json={"auth_token": "asdfsdfasdfasdfasdfasdf"},
    )


async def test_client_basic_http_request(indico_request, auth, indico_test_config):
    client = await AsyncIndicoClient(config=indico_test_config).create()

    indico_request("get", "/users/details", json={"test": True})
    response = await client.call(
        HTTPRequest(method=HTTPMethod.GET, path="/users/details")
    )
    assert response == {"test": True}
    await client.cleanup()

    async with AsyncIndicoClient(config=indico_test_config) as client:

        response = await client.call(
            HTTPRequest(method=HTTPMethod.GET, path="/users/details")
        )
        assert response == {"test": True}

async def test_client_creation_error_handling(indico_test_config):
    client = AsyncIndicoClient()
    with pytest.raises(IndicoError):
        await client.call(
            HTTPRequest(method=HTTPMethod.GET, path="/users/details")
        )

async def test_client_graphql_text_request(indico_request, auth, indico_test_config):
    client = await AsyncIndicoClient(config=indico_test_config).create()
    indico_request("post", "/graph/api/graphql", json={"data": {"datasets": []}})
    response = await client.call(
        GraphQLRequest(
            query="query list_datasets($ids: List(Int)) { datasets(ids: $ids) { id } }",
            variables={"ids": [1, 2, 3, 4]},
        )
    )
    assert response == {"datasets": []}
