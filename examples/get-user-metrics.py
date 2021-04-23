from indico import IndicoConfig, IndicoClient
from indico

"""
Example 1: User Summary
"""
# Create an Indico API client
my_config = IndicoConfig(
    host="app.indico.io", api_token_path="./path/to/indico_api_token.txt"
)
client = IndicoClient(config=my_config)
