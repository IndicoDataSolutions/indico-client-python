import os
from indico import IndicoClient, IndicoConfig

# Use environment variables
os.environ["INDICO_PROTOCOL"] = "http"
os.environ["INDICO_HOST"] = "foo.bar.com"

# Use IndicoConfig
my_config = IndicoConfig(
    host="indico.my-company.com",  # Overrides environment variable
    api_token_path="../path/to/custom_api_token.txt",
)

# Will connect to http://indico.my-company.com
client = IndicoClient(config=my_config)
