from indico.client import IndicoClient, IndicoConfig
from indico.client.request import HTTPRequest, HTTPMethod, GraphQLRequest

def test_http_request(indico):
    client = IndicoClient()
    response = client.call(HTTPRequest(method=HTTPMethod.GET, path="/auth/users/details"))
    assert "email" in response

def test_disable_cookie_domain(indico):
    client = IndicoClient(IndicoConfig(_disable_cookie_domain=True))
    response = client.call(HTTPRequest(method=HTTPMethod.GET, path="/auth/users/details"))
    assert "email" in response

def test_graphql_request(indico):
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
    assert "modelGroups" in response

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