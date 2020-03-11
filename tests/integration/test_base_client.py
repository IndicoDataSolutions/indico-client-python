from indico.client import IndicoClient
from indico.client.request import HTTPRequest, HTTPMethod, GraphQLRequest

def test_http_request():
    client = IndicoClient()
    response = client.call(HTTPRequest(method=HTTPMethod.GET, path="/auth/users/details"))
    assert "email" in response

def test_graphql_request():
    client = IndicoClient()
    response = client.call(GraphQLRequest(query="""
    query {
	    modelGroups{
            modelGroups{
                id
            }
        }
    }
    """))
    assert "data" in response
    assert "modelGroups" in response["data"]

def test_graphql_with_ids(): 
    client = IndicoClient()
    response = client.call(GraphQLRequest(
        query="""
            query modelGroupQueries($ids: [Int]) {
	            modelGroups(modelGroupIds: $ids){
                    modelGroups{
                        id
                    }
                }
            }
        """, 
        variables={"ids": [1]}
    ))
    
    assert "modelGroups" in response