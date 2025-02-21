import unittest.mock
import pytest


from indico.client import IndicoClient, HTTPRequest, HTTPMethod, GraphQLRequest
from indico.config import IndicoConfig


@pytest.fixture(scope="function")
def indico_test_config():
    return IndicoConfig(protocol="mock", host="mock")


@pytest.fixture(scope="function")
def indico_request(requests_mock, indico_test_config):
    def new_request_mock(method, path, *args, **kwargs):
        config = indico_test_config
        url = f"{config.protocol}://{config.host}" + path
        getattr(requests_mock, method)(
            url, *args, **kwargs, headers={"Content-Type": "application/json"}
        )

    return new_request_mock


@pytest.fixture(scope="function")
def auth(indico_request):
    indico_request(
        "post",
        "/auth/users/refresh_token",
        json={"auth_token": "asdfsdfasdfasdfasdfasdf"},
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
        additional_matcher=lambda r: r.verify,
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
        additional_matcher=lambda r: not r.verify,
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
        additional_matcher=lambda r: not r.verify,
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
        additional_matcher=lambda r: r.verify,
        json={"data": {"datasets": []}},
    )
    response = client.call(
        GraphQLRequest(
            query="query getIPAVersion {\n  ipaVersion\n}\n",
        )
    )
    assert response == {"datasets": []}
