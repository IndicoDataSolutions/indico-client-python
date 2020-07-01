from indico import IndicoClient
from indico.queries import GetModelGroup, GetTrainingModelWithProgress

# The model group ID can be found on the review page of the indico platform
model_group_id = 4305

client = IndicoClient()

# Get the model group and training status
mg = client.call(GetModelGroup(model_group_id))
training_mg = client.call(GetTrainingModelWithProgress(model_group_id))

print(f"Model Name: {mg.name}")
print(f"Training status: {training_mg.status}")
print(f"Percent complete: {training_mg.training_progress.percent_complete:.2f}")
