import pytest
import time
from pathlib import Path
from indico.client import IndicoClient
from indico.queries.datasets import CreateDataset
import os


@pytest.fixture(scope="module")
def airlines_dataset(indico):
    client = IndicoClient()
    dataset_filepath = str(Path(__file__).parents[0]) + "/AirlineComplaints.csv"
    
    response = client.call(CreateDataset(name=f"AirlineComplaints-test-{int(time.time())}", files=[dataset_filepath]))
    assert response.status == "COMPLETE"
    return response