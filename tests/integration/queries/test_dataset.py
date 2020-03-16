import time
from pathlib import Path
from indico.client import IndicoClient
from indico.queries.datasets import GetDataset, GetDatasetFileStatus, CreateDataset
from indico.types.dataset import Dataset

def test_create_dataset(indico):
    client = IndicoClient()
    dataset_filepath = str(Path(__file__).parents[1]) + "/data/AirlineComplaints.csv"
    
    response = client.call(CreateDataset(name=f"AirlineComplaints-test-{int(time.time())}", files=[dataset_filepath]))

    assert type(response) == Dataset
    assert response.status == "COMPLETE"
    assert type(response.id) == int 


def test_get_datasets(indico): 
    client = IndicoClient()
    dataset = client.call(GetDataset(id=773))
    
    assert type(dataset) == Dataset
    assert dataset.id == 773

def test_get_dataset_file_status(indico):
    client = IndicoClient()
    dataset = client.call(GetDatasetFileStatus(id=773))
    
    assert type(dataset) == Dataset
    assert dataset.id == 773
    assert len(dataset.files) > 0 
    assert dataset.files[0].status != None
