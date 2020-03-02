# Indico IPA platform Client
### A python client library for the [Indico IPA Platform](https://app.indico.io/).

# Installation
--------------
From PyPI:
```bash
pip3 install indico-client
```

From source:
```bash
git clone https://github.com/IndicoDataSolutions/indicoio-py.git
python3 setup.py install
```

Running in a Docker container:
```
docker build -t indico-client .
docker run -it indico-client bash
```

# Getting Started

First, download an API token from your [user dashboard](https://app.indico.io/auth/user), and save the downloaded file as `indico_api_token.txt` in either your home directory or working directory.

## API Examples
```python3
import indico
from indico import IndicoClient
from indico.queries.model_groups import ListModelGroups, ModelGroupPredict
from indico.queries.job import JobResult
from indico.types import JobStatus

indico = IndicoClient()
mg = indico.call(ListModelGroups(ids=[1234]))[0]

data = ["Test example", "Test example 2"]
job = indico.call(ModelGroupPredict(model_group=mg, data=data))

job = indico.call(JobResult(job=job, wait=True))

print(job.result())
```
``` python3 
import indico
from indico import IndicoClient
from indico.queries.documents import DocumentExtraction
from indico.queries.job import JobResult
from indico.types import JobStatus
from indico.storage import RetrieveStorageObject

indico = IndicoClient()
job = indico.call(DocumentExtraction(files=[open("test.pdf", 'r'), config={"preset": "legacy"}])
job = indico.call(JobResult(job=job, wait=True))

so = job.result()

json_data = indico.call(RetrieveStorageObject(so))
print(json_data)

## API example asyncio

