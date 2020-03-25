import time
from pathlib import Path
from indico.client import IndicoClient
from indico.queries.datasets import GetDataset, GetDatasetFileStatus, CreateDataset, ListDatasets
from indico.types.dataset import Dataset
from tests.integration.data.datasets import airlines_dataset

def test_create_dataset(indico):
    client = IndicoClient()
    dataset_filepath = str(Path(__file__).parents[1]) + "/data/AirlineComplaints.csv"
    
    response = client.call(CreateDataset(name=f"AirlineComplaints-test-{int(time.time())}", files=[dataset_filepath]))

    assert type(response) == Dataset
    assert response.status == "COMPLETE"
    assert type(response.id) == int 


def test_get_datasets(indico, airlines_dataset): 
    client = IndicoClient()
    dataset = client.call(GetDataset(id=airlines_dataset.id))
    
    assert type(dataset) == Dataset
    assert dataset.id == airlines_dataset.id

def test_get_dataset_file_status(indico, airlines_dataset):
    client = IndicoClient()
    dataset = client.call(GetDatasetFileStatus(id=airlines_dataset.id))
    
    assert type(dataset) == Dataset
    assert dataset.id == airlines_dataset.id
    assert len(dataset.files) > 0 
    assert dataset.files[0].status != None

def test_list_datasets(indico, airlines_dataset):
    client = IndicoClient()
    datasets = client.call(ListDatasets(limit=1))

    assert type(datasets) == list
    assert len(datasets) == 1
    assert type(datasets[0]) == Dataset

    
