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
from indico.queries.model_groups.metrics import (
    AnnotationModelGroupMetrics,
    ObjectDetectionMetrics,
    GetModelGroupMetrics,
)
from indico.queries.storage import UploadDocument, URL_PREFIX
from indico.queries.jobs import JobStatus
from indico.types.dataset import Dataset
from indico.types.model_group import ModelGroup
from indico.types.model import Model, TrainingProgress
from ..data.datasets import (
    airlines_dataset,
    too_small_dataset,
    airlines_model_group,
    cats_dogs_image_dataset,
    cats_dogs_modelgroup,
    org_annotate_model_group,
    org_annotate_dataset,
)
from indico.errors import IndicoNotFound, IndicoRequestError


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


def test_get_missing_model_group(indico):
    client = IndicoClient()

    with pytest.raises(IndicoNotFound):
        client.call(GetModelGroup(id=500000))


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


def test_create_model_group_with_wait_not_enough_data(indico, too_small_dataset):
    client = IndicoClient()

    name = f"TestCreateModelGroup-{int(time.time())}"
    mg: ModelGroup = client.call(
        CreateModelGroup(
            name=name,
            dataset_id=too_small_dataset.id,
            source_column_id=too_small_dataset.datacolumn_by_name("Text").id,
            labelset_id=too_small_dataset.labelset_by_name("Target_1").id,
            wait=True,
        )
    )

    assert mg.name == name
    assert mg.selected_model.status == "NOT_ENOUGH_DATA"


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
    base_dir = Path(__file__).parent.parent / "data"
    image_filepaths = [os.path.join(base_dir, fname) for fname in image_fnames]
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
            model_id=cats_dogs_modelgroup.selected_model.id,
            data=storage_urls,
            predict_options={"threshold": 0.25, "crops": True},
            load=False,
        )
    )
    assert type(job.id) == str

    result = client.call(JobStatus(job.id, wait=True))

    assert result.status != "FAILURE"
    assert len(result.result) == 5
    assert result.result[0][0].get("image")["url"].startswith(URL_PREFIX)


def test_load_model(indico, airlines_dataset, airlines_model_group):
    client = IndicoClient()

    status = client.call(LoadModel(model_id=airlines_model_group.selected_model.id,))

    assert status == "ready"


def test_annotation_metrics(indico, org_annotate_dataset, org_annotate_model_group):
    client = IndicoClient()
    result = client.call(
        AnnotationModelGroupMetrics(model_group_id=org_annotate_model_group.id)
    )
    check_annotation_metrics(result)


def test_object_detection_metrics(
    indico, cats_dogs_image_dataset, cats_dogs_modelgroup
):
    client = IndicoClient()
    result = client.call(ObjectDetectionMetrics(cats_dogs_modelgroup.id))
    for metric_type in ["AP", "AP-Cat", "AP-Dog\n", "AP50", "AP75"]:
        assert isinstance(result["bbox"][metric_type], float)


def test_object_detection_metrics_bad_id(indico):
    from indico import IndicoConfig
    client = IndicoClient()
    with pytest.raises(IndicoRequestError):
        _ = client.call(ObjectDetectionMetrics(-1))


def test_model_group_metrics_query(
    indico, org_annotate_dataset, org_annotate_model_group
):
    client = IndicoClient()
    result = client.call(
        GetModelGroupMetrics(model_group_id=org_annotate_model_group.id)
    )
    check_annotation_metrics(result)


def check_annotation_metrics(result):
    assert result.class_metrics[0].name == "org"
    for attr in [
        "f1_score",
        "false_negatives",
        "false_positives",
        "precision",
        "recall",
        "true_positives",
    ]:
        assert isinstance(
            getattr(result.class_metrics[0].metrics[0], attr), (float, int)
        )
    assert isinstance(result.class_metrics[0].metrics[0].span_type, str)

    assert isinstance(result.model_level_metrics[0].span_type, str)
    assert isinstance(result.model_level_metrics[0].micro_f1, float)
    assert isinstance(result.model_level_metrics[0].macro_f1, float)
    assert isinstance(result.model_level_metrics[0].weighted_f1, float)
    assert result.retrain_for_metrics is False
