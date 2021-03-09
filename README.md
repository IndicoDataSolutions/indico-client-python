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

### Getting Classification/Extraction Results
```python3
from indico import IndicoClient, IndicoConfig
from indico.queries import JobStatus, ModelGroupPredict

config = IndicoConfig(
    host='app.indico.io', # or your custom app location
    api_token_path='./indico_api_token.txt' # path to your API token
    )
client = IndicoClient(config=config)

data = ["Test example", "Test example 2"]
job = client.call(ModelGroupPredict(model_id=32777, data=data))

prediction = client.call(JobStatus(id=job.id, wait=True))

print(prediction.result)
```

### Performing OCR / Document Text and Data Extraction
``` python3 
from indico import IndicoClient, IndicoConfig
from indico.queries import DocumentExtraction, JobStatus, RetrieveStorageObject

config = IndicoConfig(
    host='app.indico.io',
    api_token_path='./indico_api_token.txt'
    )

client = IndicoClient(config=config)
file_paths = ['./test_data.pdf', './test_data2.pdf']
job = client.call(
    DocumentExtraction(
        files=file_paths, 
        json_config={"preset_config": "ondocument"} # see full docs for config options
        )
    )
# job is a list object with length equal to # of files, retrieve each extraction by 
# its index- below, we're retrieving the first extraction in file_paths

job_file = client.call(JobStatus(id=job[0].id, wait=True))
result = client.call(RetrieveStorageObject(job_file.result))
print(result)
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

# Contributing

This repository adheres (as best as possible) to the following standards:
 - Python Black Formatter
    - Line Width=88
 - [Google Docstrings](https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html)
