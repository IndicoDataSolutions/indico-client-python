from indico import IndicoClient, IndicoConfig
from indico.queries import GetDataset, CreateExport, DownloadExport
import pandas as pd


"""Example 1: Create export from dataset and download as csv"""

dataset_id = 6826

# Create an Indico API client
my_config = IndicoConfig(
    host="app.indico.io", api_token_path="./path/to/indico_api_token.txt"
)
client = IndicoClient(config=my_config)

# Get dataset object
dataset = client.call(GetDataset(id=dataset_id))

# Create export object using dataset's id and labelset id
export = client.call(
            CreateExport(
                dataset_id=dataset.id,
                labelset_id=dataset.labelsets[0].id,
                wait=True
            )
        )

# Use export object to download as pandas csv
csv = client.call(DownloadExport(export.id))
