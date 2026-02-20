import pytest

from indico.client import GraphQLRequest, HTTPMethod, HTTPRequest, IndicoClient
from indico.config import IndicoConfig


@pytest.fixture(scope="function")
def indico_test_config():
    return IndicoConfig(protocol="mock", host="mock")


@pytest.fixture(scope="function")
def indico_request(indico_test_config, mocker):
    registered = {}

    def _mock_make_request(self, method, path, *args, **kwargs):
        if (method, path) in registered:
            return registered[(method, path)]
        raise Exception(f"Unmocked {method} {path}")

    mocker.patch(
        "indico.http.client.HTTPClient._make_request",
        _mock_make_request,
    )

    def new_request_mock(method, path, json=None, additional_matcher=None):
        registered[(method, path)] = json

    return new_request_mock


@pytest.fixture(scope="function")
def auth(indico_request):
    indico_request(
        "post",
        "/auth/users/refresh_token",
        json={"auth_token": "asdfsdfasdfasdfasdfasdfasdf"},
    )


def test_client_basic_http_request(indico_request, auth, indico_test_config):
    client = IndicoClient(config=indico_test_config)

    indico_request("get", "/users/details", json={"test": True})
    response = client.call(HTTPRequest(method=HTTPMethod.GET, path="/users/details"))
    assert response == {"test": True}


def test_client_graphql_text_request(indico_request, auth, indico_test_config):
    client = IndicoClient(config=indico_test_config)
    indico_request("post", "/graph/api/graphql", json={"data": {"datasets": []}})
    response = client.call(
        GraphQLRequest(
            query="query list_datasets($ids: List(Int)) { datasets(ids: $ids) { id } }",
            variables={"ids": [1, 2, 3, 4]},
        )
    )
    assert response == {"datasets": []}


def test_client_verify_true_request(indico_request, auth, indico_test_config):
    client = IndicoClient(indico_test_config)
    indico_request(
        "post",
        "/graph/api/graphql",
        json={"data": {"datasets": []}},
    )

    response = client.call(
        GraphQLRequest(
            query="query list_datasets($ids: List(Int)) { datasets(ids: $ids) { id } }",
            variables={"ids": [1, 2, 3, 4]},
        )
    )
    assert response == {"datasets": []}


def test_client_verify_false_request(indico_request, auth, indico_test_config):
    client = IndicoClient(
        IndicoConfig(
            verify_ssl=False,
            host=indico_test_config.host,
            protocol=indico_test_config.protocol,
        )
    )
    indico_request(
        "post",
        "/graph/api/graphql",
        json={"data": {"datasets": []}},
    )

    response = client.call(
        GraphQLRequest(
            query="query list_datasets($ids: List(Int)) { datasets(ids: $ids) { id } }",
            variables={"ids": [1, 2, 3, 4]},
        )
    )
    assert response == {"datasets": []}


def test_client_requests_params(indico_request, auth, indico_test_config):
    client = IndicoClient(
        IndicoConfig(
            requests_params={"verify": False},
            host=indico_test_config.host,
            protocol=indico_test_config.protocol,
        )
    )
    indico_request(
        "post",
        "/graph/api/graphql",
        json={"data": {"datasets": []}},
    )
    response = client.call(
        GraphQLRequest(
            query="query list_datasets($ids: List(Int)) { datasets(ids: $ids) { id } }",
            variables={"ids": [1, 2, 3, 4]},
        )
    )
    assert response == {"datasets": []}


def test_client_get_ipa_version(indico_request, auth, indico_test_config):
    client = IndicoClient(config=indico_test_config)
    indico_request(
        "post",
        "/graph/api/graphql",
        json={"data": {"datasets": []}},
    )
    response = client.call(
        GraphQLRequest(
            query="query getIPAVersion {\n  ipaVersion\n}\n",
        )
    )
    assert response == {"datasets": []}
