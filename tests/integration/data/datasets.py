import os
import pytest
import time
from pathlib import Path
from indico.client import IndicoClient
from indico.queries import CreateDataset, CreateModelGroup
from indico.types import ModelGroup, Dataset


@pytest.fixture(scope="module")
def airlines_dataset(indico):
    client = IndicoClient()
    dataset_filepath = str(Path(__file__).parents[0]) + "/AirlineComplaints.csv"

    response = client.call(
        CreateDataset(
            name=f"AirlineComplaints-test-{int(time.time())}", files=[dataset_filepath]
        )
    )
    assert response.status == "COMPLETE"
    return response


@pytest.fixture(scope="module")
def too_small_dataset(indico):
    client = IndicoClient()
    dataset_filepath = str(Path(__file__).parents[0]) + "/TooSmall.csv"

    response = client.call(
        CreateDataset(
            name=f"TooSmall-test-{int(time.time())}", files=[dataset_filepath]
        )
    )
    assert response.status == "COMPLETE"
    return response


@pytest.fixture(scope="module")
def airlines_model_group(indico, airlines_dataset: Dataset) -> ModelGroup:
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
    return mg


@pytest.fixture(scope="module")
def cats_dogs_image_dataset(indico):
    client = IndicoClient()
    dataset_filepath = str(Path(__file__).parents[0]) + "/dog_vs_cats_small.csv"

    response = client.call(
        CreateDataset(
            name=f"DogsAndCats-test-{int(time.time())}",
            files=dataset_filepath,
            from_local_images=True,
        )
    )
    assert response.status == "COMPLETE"
    return response


@pytest.fixture(scope="module")
def cats_dogs_modelgroup(indico, cats_dogs_image_dataset: Dataset) -> ModelGroup:
    client = IndicoClient()
    name = f"TestCreateObjectDetectionMg-{int(time.time())}"

    model_training_options = {
        "max_iter": 20,
        "lr": 0.1,
        "batch_size": 1,
        "filter_empty": False,
        "test_size": 0.2,
        "use_small_model": True,
    }

    mg: ModelGroup = client.call(
        CreateModelGroup(
            name=name,
            dataset_id=cats_dogs_image_dataset.id,
            source_column_id=cats_dogs_image_dataset.datacolumn_by_name("urls").id,
            labelset_id=cats_dogs_image_dataset.labelset_by_name("label").id,
            model_training_options=model_training_options,
            wait=True,
        )
    )
    return mg


@pytest.fixture(scope="module")
def org_annotate_dataset(indico):
    client = IndicoClient()
    dataset_filepath = str(Path(__file__).parents[0]) + "/org-annotate-labeled.csv"

    response = client.call(
        CreateDataset(
            name=f"OrgAnnotate-test-{int(time.time())}", files=[dataset_filepath]
        )
    )
    assert response.status == "COMPLETE"
    return response


@pytest.fixture(scope="module")
def org_annotate_model_group(indico, org_annotate_dataset: Dataset) -> ModelGroup:
    client = IndicoClient()
    name = f"TestFinetuneModelGroup-{int(time.time())}"
    mg: ModelGroup = client.call(
        CreateModelGroup(
            name=name,
            dataset_id=org_annotate_dataset.id,
            source_column_id=org_annotate_dataset.datacolumn_by_name(
                "News Headlines w/Company Names"
            ).id,
            labelset_id=org_annotate_dataset.labelset_by_name("question_825").id,
            wait=True,
        )
    )
    return mg
