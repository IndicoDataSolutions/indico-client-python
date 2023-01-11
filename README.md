# Indico IPA platform Client
### A python client library for the [Indico IPA Platform](https://app.indico.io/).
### See the full [Documentation](https://indicodatasolutions.github.io/indico-client-python/).

# Installation
--------------
Required: Python 3.6, 3.7, or 3.8

From PyPI:
```bash
pip3 install indico-client
```

From source:
```bash
git clone https://github.com/IndicoDataSolutions/indico-client-python.git
python3 setup.py install
```

Running in a Docker container:
```
docker build -t indico-client .
docker run -it indico-client bash
```

# Getting Started

## Authentication 

The Indico Platform and Client Libraries use JSON Web Tokens (JWT) for user 
authentication. You can download a token from your [user dashboard](https://app.indico.io/auth/user) by clicking the 
large, blue “Download new API Token” button. Most browsers will download the API token 
as indico_api_token.txt and place it in your Downloads directory. You should move the 
token file from Downloads to either your home directory or another location in your 
development environment.



## API Examples

### Creating a Client
```python3
from indico import IndicoClient, IndicoConfig

config = IndicoConfig(
    host='app.indico.io', # or your custom app location
    api_token_path='./indico_api_token.txt' # path to your API token
    )
client = IndicoClient(config=config)
```
### Pure GraphQL example
```
from indico import IndicoClient
from indico.client.request import GraphQLRequest

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

model_groups = response["model_groups"]["model_groups"]
```

# Testing the SDK

To run the tests associated with this repo perform the following:
### Prerequisite
Set the `INDICO_API_TOKEN` environment variable to the token of the environment you need to run tests against.
`export INDICO_API_TOKEN=<api_token>

### Running the tests
1. Create a virtual environment
`python3 -m venv venv`
2. Activate the virtual environment
`source venv/bin/activate`
3. Install the client
`python3 setup.py install`
4. Install pytest
`pip3 install pytest`
5. Run tests
`pytest -sv --host <indico_host> tests/`
    * Only run unit tests `pytest -sv --host <indico_host> tests/unit/`
    * Only run integration tests `pytest -sv --host <indico_host> tests/integration/`


# Contributing

This repository adheres (as best as possible) to the following standards:
 - Python Black Formatter
    - Line Width=88
 - [Google Docstrings](https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html)
