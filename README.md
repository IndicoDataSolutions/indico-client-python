# Indico IPA platform API
### A python client library for the [Indico IPA Platform](https://app.indico.io/).

# Installation
--------------
From PyPI:
```bash
pip3 install indicoio
```

From source:
```bash
git clone https://github.com/IndicoDataSolutions/indicoio-py.git
python3 setup.py install
```

Running in a Docker container:
```
docker build -t indicoio .
docker run -it indicoio bash
```

# Getting Started

First, download an API token from your [user dashboard](https://app.indico.io/auth/user), and save the downloaded file as `indico_api_token.txt` in either your home directory or working directory.

## API Examples
```python3
import indicoio
from indicoio import ModelGroup, IndicoApi

# Model Predictions
mg = ModelGroup(id=<model group id>)
mg.load()
mg.predict(["some text"])

# PDF Extraction
api_client = IndicoApi()
api_client.pdf_extraction(["url or file"], **options)
```