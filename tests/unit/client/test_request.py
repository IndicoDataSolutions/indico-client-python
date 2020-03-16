import pytest

from indico.client.request import HTTPMethod, HTTPRequest, GraphQLRequest


def test_http_request_properties():
    data = {"test", "something"}
    path = "/something/api/test"
    req = HTTPRequest(method=HTTPMethod.GET, path=path, data=data)

    assert req.data == data
    assert req.path == path
    assert req.method == HTTPMethod.GET

def test_http_request_process_response():
    data = {"test", "something"}
    path = "/something/api/test"
    req = HTTPRequest(method=HTTPMethod.GET, path=path, data=data)

    assert req.process_respone(data) == data

def test_graphql_request_properties():
    query = "query($ids: List(Int)) { dataset(ids: $ids) { name } }"
    variables = {"ids": [1,2,3,4]}

    req = GraphQLRequest(query=query, variables=variables)

    assert req.path == "/graph/api/graphql"
    assert req.method == HTTPMethod.POST
    assert req.data == {"query": query, "variables": variables}