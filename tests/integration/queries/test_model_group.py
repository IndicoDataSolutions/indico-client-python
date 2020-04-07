import pytest
import time
import os
import json
from pathlib import Path
from indico.client import IndicoClient
from indico.queries.model_groups import (
    GetModelGroup,
    CreateModelGroup,
    ModelGroupPredict,
    GetTrainingModelWithProgress,
    LoadModel,
)
from indico.queries.storage import UploadDocument, URL_PREFIX
from indico.queries.jobs import JobStatus
from indico.types.dataset import Dataset
from indico.types.model_group import ModelGroup
from indico.types.model import Model, TrainingProgress
from ..data.datasets import (
    airlines_dataset,
    airlines_model_group,
    cats_dogs_image_dataset,
    cats_dogs_modelgroup,
)
from indico.errors import IndicoNotFound


def test_create_model_group(airlines_dataset: Dataset):
    client = IndicoClient()

    name = f"TestCreateModelGroup-{int(time.time())}"
    mg: ModelGroup = client.call(
        CreateModelGroup(
            name=name,
            dataset_id=airlines_dataset.id,
            source_column_id=airlines_dataset.datacolumn_by_name("Text").id,
            labelset_id=airlines_dataset.labelset_by_name("Target_1").id,
        )
    )

    assert mg.name == name


def test_object_detection(cats_dogs_image_dataset: Dataset):
    client = IndicoClient()
    name = f"TestCreateObjectDetectionMg-{int(time.time())}"

    model_training_options = {
        "max_iter": 2000,
        "lr": 0.1,
        "batch_size": 1,
        "filter_empty": False,
        "test_size": 0.2,
        "use_small_model": False,
    }

    mg: ModelGroup = client.call(
        CreateModelGroup(
            name=name,
            dataset_id=cats_dogs_image_dataset.id,
            source_column_id=cats_dogs_image_dataset.datacolumn_by_name("urls").id,
            labelset_id=cats_dogs_image_dataset.labelset_by_name("label").id,
            model_training_options=model_training_options,
        )
    )

    assert mg.name == name


def test_create_model_group_with_wait(indico, airlines_dataset: Dataset):
    client = IndicoClient()

    name = f"TestCreateModelGroup-{int(time.time())}"
    mg: ModelGroup = client.call(
        CreateModelGroup(
            name=name,
            dataset_id=airlines_dataset.id,
            source_column_id=airlines_dataset.datacolumn_by_name("Text").id,
            labelset_id=airlines_dataset.labelset_by_name("Target_1").id,
            wait=True,
        )
    )

    assert mg.name == name
    assert mg.selected_model.status == "COMPLETE"


def test_model_group_progress(indico, airlines_dataset: Dataset):
    client = IndicoClient()

    name = f"TestCreateModelGroup-{int(time.time())}"
    mg: ModelGroup = client.call(
        CreateModelGroup(
            name=name,
            dataset_id=airlines_dataset.id,
            source_column_id=airlines_dataset.datacolumn_by_name("Text").id,
            labelset_id=airlines_dataset.labelset_by_name("Target_1").id,
            wait=False,
        )
    )
    time.sleep(1)
    model: Model = client.call((GetTrainingModelWithProgress(id=mg.id)))

    assert type(model) == Model
    assert model.status in ["CREATING", "TRAINING", "COMPLETE"]
    assert type(model.training_progress) == TrainingProgress
    assert model.training_progress.percent_complete < 101.0


def test_model_group_progress_bad_model_group_id(indico, airlines_dataset: Dataset):
    client = IndicoClient()

    with pytest.raises(IndicoNotFound):
        client.call((GetTrainingModelWithProgress(id=-1)))


def test_predict(indico, airlines_dataset, airlines_model_group):
    client = IndicoClient()

    job = client.call(
        ModelGroupPredict(
            model_id=airlines_model_group.selected_model.id,
            data=["I hate this airline"],
        )
    )

    assert type(job.id) == str

    job = client.call(JobStatus(id=job.id, wait=True))
    assert len(job.result) == 1


def get_storage_urls_from_fnames(client, image_fnames):
    client = IndicoClient()
    image_filenames = ["1.jpg", "2.jpg", "3.jpg", "4.jpg", "5.jpg"]
    base_dir = Path(__file__).parent.parent / "data"
    image_filepaths = [os.path.join(base_dir, fname) for fname in image_filenames]
    response = client.call(UploadDocument(files=image_filepaths))
    storage_urls = [URL_PREFIX + json.loads(r["filemeta"])["path"] for r in response]
    return storage_urls


def test_object_detection_predict_storage(
    indico, cats_dogs_image_dataset, cats_dogs_modelgroup
):
    client = IndicoClient()
    storage_urls = get_storage_urls_from_fnames(
        client, ["1.jpg", "2.jpg", "3.jpg", "4.jpg", "5.jpg"]
    )
    job = client.call(
        ModelGroupPredict(
            model_id=cats_dogs_modelgroup.selected_model.id, data=storage_urls
        )
    )

    assert type(job.id) == str

    result = client.call(JobStatus(job.id, wait=True))

    assert result.status != "FAILURE"
    assert len(result.result) == 5


def test_load_model(indico, airlines_dataset, airlines_model_group):
    client = IndicoClient()

    status = client.call(LoadModel(model_id=airlines_model_group.selected_model.id,))

    assert status == "ready"
