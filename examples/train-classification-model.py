from indico import IndicoClient, IndicoConfig
from indico.queries import (
    AddModelGroupComponent,
    CreateDataset,
    GetModelGroupSelectedModelStatus,
    JobStatus,
    ModelGroupPredict,
)

# Create an Indico API client
from indico.types import Workflow

my_config = IndicoConfig(
    host="try.indico.io", api_token_path="./path/to/indico_api_token.txt"
)
client = IndicoClient(config=my_config)

# create the dataset
dataset = client.call(
    CreateDataset(name="airline_comments", files=["./airline-comments.csv"])
)

updated_workflow: Workflow = client.call(
    AddModelGroupComponent(
        name="my_classification_model",
        dataset_id=dataset.id,
        source_column_id=dataset.datacolumn_by_name("text").id,  # csv text column
        labelset_id=dataset.labelset_by_name("Target_1").id,  # csv target class column
    )
)

model_group = updated_workflow.model_group_by_name("my_classification_model")
status = client.call(GetModelGroupSelectedModelStatus(id=model_group.id))
while status not in ["FAILED", "COMPLETE", "NOT_ENOUGH_DATA"]:
    status = client.call(GetModelGroupSelectedModelStatus(id=model_group.id))

# predict on the model
job = client.call(
    ModelGroupPredict(
        model_id=model_group.selected_model.id,
        data=["Sample Text to predict on", "More Sample text to predict on"],
    )
)

# retrieve your prediction results
predictions = client.call(JobStatus(id=job.id, wait=True)).result
