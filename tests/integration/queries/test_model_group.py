import pytest
import time
from indico.client import IndicoClient
from indico.queries.model_groups import GetModelGroup, CreateModelGroup, ModelGroupPredict, GetTrainingModelWithProgress
from indico.queries.jobs import JobStatus
from indico.types.dataset import Dataset
from indico.types.model_group import ModelGroup
from indico.types.model import Model, TrainingProgress
from ..data.datasets import airlines_dataset
from indico.errors import IndicoNotFound
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


def test_model_group_progress(indico, airlines_dataset: Dataset):
    client = IndicoClient()
    
    name = f"TestCreateModelGroup-{int(time.time())}"
    mg: ModelGroup = client.call(CreateModelGroup(
        name=name,
        dataset_id=airlines_dataset.id,
        source_column_id=airlines_dataset.datacolumn_by_name("Text").id,
        labelset_id=airlines_dataset.labelset_by_name("Target_1").id,
        wait=False
    ))
    time.sleep(1)
    model: Model = client.call((GetTrainingModelWithProgress(id=mg.id)))

    assert type(model) == Model
    assert model.status in ["CREATING", "TRAINING", "COMPLETE"]
    assert type(model.training_progress) == TrainingProgress
    assert model.training_progress.percent_complete  < 101.0

def test_model_group_progress_bad_model_group_id(indico, airlines_dataset: Dataset):
    client = IndicoClient()

    with pytest.raises(IndicoNotFound):
        client.call((GetTrainingModelWithProgress(id=-1)))

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
