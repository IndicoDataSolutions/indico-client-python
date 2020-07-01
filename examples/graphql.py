from indico import IndicoClient
from indico.queries import GraphQLRequest


client = IndicoClient()

# GraphQL Query to list my datasets
qstr = """{
            datasets {
                id
                name
                status
                rowCount
                numModelGroups
                modelGroups {
                    id
                }
            }
        }"""

response = client.call(GraphQLRequest(query=qstr))
print(response)
