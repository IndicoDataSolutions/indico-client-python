from indico import IndicoClient, IndicoConfig
from indico.queries import GraphQLRequest

my_config = IndicoConfig(
    host="try.indico.io", api_token_path="./path/to/indico_api_token.txt"
)

client = IndicoClient(config=my_config)

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
