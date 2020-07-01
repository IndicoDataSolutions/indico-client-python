from indico import IndicoClient
from indico.queries import CreateDataset, CreateModelGroup, ModelGroupPredict, JobStatus

client = IndicoClient()

# Create the dataset
dataset = client.call(
    CreateDataset(name="airline_comments", files=["./airline-comments.csv"])
)

# Train the model w/ the relevant csv columns
model_group = client.call(
    CreateModelGroup(
        name="my_classification_model",
        dataset_id=dataset.id,
        source_column_id=dataset.datacolumn_by_name("text").id,  # csv text column
        labelset_id=dataset.labelset_by_name(
            "Target_1"
        ).id,  # csv target class column
        wait=True,  # wait for training to finish
    )
)


# Predict on the model
job = client.call(
    ModelGroupPredict(
        model_id=model_group.selected_model.id,
        data=["Sample Text to predict on", "More Sample text to predict on"],
    )
)

# Retrieve your prediction results
predictions = client.call(JobStatus(id=job.id, wait=True)).result
