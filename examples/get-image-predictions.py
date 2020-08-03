"""
Getting Image Predictions

Image Predictions work slightly differently from generating predictions from text documents
in that they require you to first upload the documents. The script below provides a sample. 
"""
from indico import IndicoClient, IndicoConfig
from indico.queries import ModelGroupPredict, UploadImages, JobStatus

config = IndicoConfig(host="app.indico.io", api_token_path="./indico_api_token.txt")
client = IndicoClient(config)

# UploadImages returns a list of upload URLs that you can use for gathering predictions
urls = client.call(UploadImages(files=["./path/to/image.png", "./path/to/image2.png"]))

# Get your Selected Model ID (from the model's Explain page in the app or using the API)
job = client.call(ModelGroupPredict(model_id=30970, data=urls))

# Wait for the predictions to finish
predictions = client.call(JobStatus(job.id))

# Prediction results are ready
print(predictions.result)
