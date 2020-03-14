import time
from indico.client import IndicoClient
from indico.queries.model_groups import GetModelGroup, CreateModelGroup
from indico.types.dataset import Dataset
from indico.types.model_group import ModelGroup
from ..data.datasets import airlines_dataset

def test_create_model_group(airlines_dataset: Dataset):
    client = IndicoClient()
    
    name = f"TestCreateModelGroup-{int(time.time())}"
    mg: ModelGroup = client.call(CreateModelGroup(
        name=name,
        dataset_id=airlines_dataset.id,
        source_column_id=airlines_dataset.datacolumn_by_name("Text").id,
        labelset_id=airlines_dataset.datacolumn_by_name("Target_1").id
    ))

    assert mg.name == name

def test_create_model_group_with_wait(airlines_dataset: Dataset):
    client = IndicoClient()
    
    name = f"TestCreateModelGroup-{int(time.time())}"
    mg: ModelGroup = client.call(CreateModelGroup(
        name=name,
        dataset_id=airlines_dataset.id,
        source_column_id=airlines_dataset.datacolumn_by_name("Text").id,
        labelset_id=airlines_dataset.datacolumn_by_name("Target_1").id,
        wait=True
    ))

    assert mg.name == name
    assert mg.selected_model.status == "COMPLETE"




