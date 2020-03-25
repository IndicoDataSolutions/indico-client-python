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
    
    response = client.call(CreateDataset(name=f"AirlineComplaints-test-{int(time.time())}", files=[dataset_filepath]))
    assert response.status == "COMPLETE"
    return response

@pytest.fixture(scope="module")
def airlines_model_group(indico, airlines_dataset: Dataset) -> ModelGroup:
    client = IndicoClient()
    name = f"TestCreateModelGroup-{int(time.time())}"
    mg: ModelGroup = client.call(CreateModelGroup(
        name=name,
        dataset_id=airlines_dataset.id,
        source_column_id=airlines_dataset.datacolumn_by_name("Text").id,
        labelset_id=airlines_dataset.labelset_by_name("Target_1").id,
        wait=True
    ))
    return mg
