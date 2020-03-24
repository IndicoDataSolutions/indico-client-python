import os
import json
from pathlib import Path

from indico import IndicoClient
from indico.config import IndicoConfig
from indico.client.request import GraphQLRequest


def main():
    # Create a config object to manually set the host and path to
    # indico_api_token.txt. By default, IndicoClient will look read
    # environment variables to find this information
    my_config = IndicoConfig(
        host='dev.indico.io',
        api_token_path=Path(__file__).parent / 'indico_api_token.txt'
    )

    client = IndicoClient(config=my_config)

    # GraphQL Query to list my datasets
    qstr = '''{
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
        }'''

    response = client.call(GraphQLRequest(query=qstr))
    print(json.dumps(response, indent=4))


if __name__ == '__main__':
    os.chdir(Path(__file__).parent)
    main()