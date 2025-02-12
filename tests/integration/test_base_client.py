import pytest

from indico.client import IndicoClient, IndicoConfig
from indico.client.request import GraphQLRequest, HTTPMethod, HTTPRequest
from indico.errors import IndicoAuthenticationFailed
from tests.integration.data.datasets import org_annotate_dataset


def test_http_request(indico):
    client = IndicoClient()
    response = client.call(
        HTTPRequest(method=HTTPMethod.GET, path="/auth/users/details")
    )
    assert "email" in response


def test_bad_token(indico):
    with pytest.raises(IndicoAuthenticationFailed):
        client = IndicoClient(IndicoConfig(api_token="askldjflkasdjf"))


def test_disable_cookie_domain(indico):
    client = IndicoClient(IndicoConfig(_disable_cookie_domain=True))
    assert client.config._disable_cookie_domain == True
    cookies = client._http.request_session.cookies
    auth_token = next(c for c in cookies if c.name == "auth_token")
    assert auth_token.domain == ""
    response = client.call(
        HTTPRequest(method=HTTPMethod.GET, path="/auth/users/details")
    )
    assert "email" in response


def test_cookie_reset(indico):
    client = IndicoClient(IndicoConfig(_disable_cookie_domain=True))
    client._http.get_short_lived_access_token()
    cookies = client._http.request_session.cookies
    auth_token = next(c for c in cookies if c.name == "auth_token")
    assert auth_token.domain == ""
    response = client.call(
        HTTPRequest(method=HTTPMethod.GET, path="/auth/users/details")
    )
    assert "email" in response


def test_graphql_request(indico):
    client = IndicoClient()
    response = client.call(
        GraphQLRequest(
            query="""
    query {
	    modelGroups{
            modelGroups{
                id
            }
        }
    }
    """
        )
    )
    assert "modelGroups" in response


def test_graphql_with_ids(org_annotate_dataset):
    client = IndicoClient()
    response = client.call(
        GraphQLRequest(
            query="""
            query datasetQueries($id: Int!) {
	            dataset(id: $id){
                    id
                }
            }
        """,
            variables={"id": org_annotate_dataset.id},
        )
    )

    assert "dataset" in response
