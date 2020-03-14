import time
from indico.client import IndicoClient
from indico.queries.model_groups import GetModelGroup, CreateModelGroup, ModelGroupPredict
from indico.queries.jobs import JobStatus
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
        labelset_id=airlines_dataset.labelset_by_name("Target_1").id
    ))

    assert mg.name == name

def test_create_model_group_with_wait(indico, airlines_dataset: Dataset):
    client = IndicoClient()
    
    name = f"TestCreateModelGroup-{int(time.time())}"
    mg: ModelGroup = client.call(CreateModelGroup(
        name=name,
        dataset_id=airlines_dataset.id,
        source_column_id=airlines_dataset.datacolumn_by_name("Text").id,
        labelset_id=airlines_dataset.labelset_by_name("Target_1").id,
        wait=True
    ))

    assert mg.name == name
    assert mg.selected_model.status == "COMPLETE"


def test_predict(indico, airlines_dataset):
    client = IndicoClient()

    name = f"TestCreateModelGroup-{int(time.time())}"
    mg: ModelGroup = client.call(CreateModelGroup(
        name=name,
        dataset_id=airlines_dataset.id,
        source_column_id=airlines_dataset.datacolumn_by_name("Text").id,
        labelset_id=airlines_dataset.labelset_by_name("Target_1").id,
        wait=True
    ))

    job = client.call(ModelGroupPredict(
        model_id=mg.selected_model.id,
        data=["I hate this airline"]
    ))

    assert type(job.id) == str

    job = client.call(JobStatus(id=job.id, wait=True))
    assert len(job.result) == 1
