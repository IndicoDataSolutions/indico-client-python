import os
import time
from pathlib import Path
from typing import List


from indico import IndicoClient
from indico.config import IndicoConfig
from indico.types import Dataset, ModelGroup
from indico.queries import CreateDataset, CreateModelGroup, ModelGroupPredict, JobStatus


def create_dataset(client) -> Dataset:
    dataset_filepath = "./airline-comments.csv"
    response = client.call(CreateDataset(name=f"AirlineComplaints-test-{int(time.time())}", files=[dataset_filepath]))
    return response


def create_model_group(client, dataset) -> ModelGroup:
    mg: ModelGroup = client.call(CreateModelGroup(
        name=f"TestCreateModelGroup-{int(time.time())}",
        dataset_id=dataset.id,
        source_column_id=dataset.datacolumn_by_name("Text").id,
        labelset_id=dataset.labelset_by_name("Target_1").id,
        wait=True   # Waits for model group to finish training 
    ))
    return mg


def predict(client: IndicoClient, model_group: ModelGroup, data: List[str]):
    job = client.call(ModelGroupPredict(
        model_id=model_group.selected_model.id,
        data=data
    ))

    return client.call(JobStatus(id=job.id, wait=True)).result


if __name__ == "__main__":
    os.chdir(Path(__file__).parent)

    config = IndicoConfig(
        host='dev.indico.io',
        api_token_path=Path(__file__).parent / 'indico_api_token.txt'
    )

    client = IndicoClient(config=config)
    dataset = create_dataset(client)
    mg = create_model_group(client, dataset)
    predict(client, mg, ["I need wifi"])

    