# Indico IPA platform Client

### A python client library for the [Indico IPA Platform](https://try.indico.io/).

### See the full [Documentation](https://indicodatasolutions.github.io/indico-client-python/).

# Installation

---

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

### Indico API token

The Indico Platform and Client Libraries use JSON Web Tokens (JWT) for user
authentication. Details on acquiring this token can be found at this [documentation](https://docs.indicodata.ai/articles/#!common-questions-publication/how-do-i-get-started-developing-with-the-indico-api/q/API%2520token/qid/3328/qp/1)

### Environment variables

The following environment variables are used for authentication in the default `IndicoClient` object

- `INDICO_HOST`: URL of the IPA instance
- `INDICO_API_TOKEN`: user token downloaded from these [directions](#indico-api-token)

## API Examples

### Creating a Client

```python3
from indico import IndicoClient, IndicoConfig

config = IndicoConfig(
    host='try.indico.io', # or your custom app location
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

Ensure you have set the environment variables detailed [here](#environment-variables)

You will also need the following env variables set for the Exchange integration tests:

- `EXCH_TENANT_ID`
- `EXCH_CLIENT_ID`
- `EXCH_CLIENT_SECRET`
- `EXCH_USER_ID`

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
   _ Only run unit tests `pytest -sv --host <indico_host> tests/unit/`
   _ Only run integration tests `pytest -sv --host <indico_host> tests/integration/`

# Contributing

This repository adheres (as best as possible) to the following standards:

- Python Black Formatter
  - Line Width=88
- [Google Docstrings](https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html)
