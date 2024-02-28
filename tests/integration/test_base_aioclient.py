import pytest

from indico.client import AsyncIndicoClient, IndicoConfig
from indico.client.request import HTTPRequest, HTTPMethod, GraphQLRequest
from indico.errors import IndicoAuthenticationFailed


pytestmark = pytest.mark.asyncio(scope="module")


async def test_http_request(indico):
    async with AsyncIndicoClient() as client:
        response = await client.call(
            HTTPRequest(method=HTTPMethod.GET, path="/auth/users/details")
        )
        assert "email" in response


async def test_bad_token(indico):
    with pytest.raises(IndicoAuthenticationFailed):
        await AsyncIndicoClient(IndicoConfig(api_token="askldjflkasdjf")).create()


async def test_graphql_request(indico):
    async with AsyncIndicoClient() as client:
        response = await client.call(
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


async def test_graphql_with_ids(aio_org_annotate_dataset):
    async with AsyncIndicoClient() as client:
        response = await client.call(
            GraphQLRequest(
                query="""
                query datasetQueries($id: Int!) {
                    dataset(id: $id){
                        id
                    }
                }
            """,
                variables={"id": aio_org_annotate_dataset.id},
            )
        )

    assert "dataset" in response
