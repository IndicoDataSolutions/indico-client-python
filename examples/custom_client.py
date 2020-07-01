import os
from indico import IndicoClient, IndicoConfig

# Will connect to https://app.indico.io
client = IndicoClient()

# Environment variables override defaults
os.environ["INDICO_PROTOCOL"] = "http"
os.environ["INDICO_HOST"] = "foo.bar.com"

# Will connect to http://foo.bar.com
client = IndicoClient()

# IndicoConfig will override environment variables and defaults
my_config = IndicoConfig(
    host="indico.my-company.com",  # Overrides environment variable
    api_token_path="../path/to/custom_api_token.txt",
)

# Will connect to http://indico.my-company.com
client = IndicoClient(config=my_config)
