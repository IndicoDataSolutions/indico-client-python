from indico.client import IndicoClient
from indico.queries.datasets import GetDataset, GetDatasetFileStatus
from indico.types.dataset import Dataset
def test_get_datasets(): 
    client = IndicoClient()
    dataset = client.call(GetDataset(id=773))
    
    assert type(dataset) == Dataset
    assert dataset.id == 773

def test_get_dataset_file_status():
    client = IndicoClient()
    dataset = client.call(GetDatasetFileStatus(id=773))
    
    assert type(dataset) == Dataset
    assert dataset.id == 773
    assert len(dataset.files) > 0 
    assert dataset.files[0].status != None
