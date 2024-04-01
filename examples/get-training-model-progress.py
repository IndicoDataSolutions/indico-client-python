from indico import IndicoClient, IndicoConfig
from indico.queries import GetModelGroup, GetTrainingModelWithProgress

# The model group ID can be found on the review page of the indico platform
model_group_id = 4305

my_config = IndicoConfig(
    host="try.indico.io", api_token_path="./path/to/indico_api_token.txt"
)

client = IndicoClient(config=my_config)

# Get the model group and training status
mg = client.call(GetModelGroup(model_group_id))
training_mg = client.call(GetTrainingModelWithProgress(model_group_id))

print(f"Model Name: {mg.name}")
print(f"Training status: {training_mg.status}")
print(f"Percent complete: {training_mg.training_progress.percent_complete:.2f}")
