import unittest.mock
import pytest

from indico.client import IndicoClient, HTTPRequest, HTTPMethod, GraphQLRequest


@pytest.fixture(scope="function")
def indico_request(requests_mock):
    def new_request_mock(method, path, *args, **kwargs):
        url = "https://app.indico.io" + path
        getattr(requests_mock, method)(url, *args, **kwargs, headers={"Content-Type": "application/json"})
    return new_request_mock


@pytest.fixture(scope="function")
def auth(indico_request):
    indico_request("post", "/auth/users/refresh_token", json={"auth_token": "asdfsdfasdfasdfasdfasdf"})


def test_client_basic_http_request(indico_request, auth):
    client = IndicoClient()

    indico_request("get", "/users/details", json={"test": True})
    response = client.call(request=HTTPRequest(method=HTTPMethod.GET, path="/users/details"))
    assert response == {"test": True}

def test_client_graphql_text_request(indico_request, auth):
    client = IndicoClient()
    indico_request("post", "/graph/api/graphql", json={"datasets": []})

    response = client.call(GraphQLRequest(query="query list_datasets($ids: List(Int)) { datasets(ids: $ids) { id } }", variables={"ids": [1,2,3,4]}))
    assert response == {"datasets": []}

