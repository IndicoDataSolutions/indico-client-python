from indico import IndicoClient, IndicoConfig
from indico.queries import DocumentExtraction, JobStatus, RetrieveStorageObject


# Create an Indico API client
my_config = IndicoConfig(
    host="app.indico.io", api_token_path="./path/to/indico_api_token.txt"
)
client = IndicoClient(config=my_config)

# OCR a single file and wait for it to complete
job = client.call(
    DocumentExtraction(
        files=["./path_to_doc.pdf"], json_config=dict(preset_config="ondocument")
    )
)
extracted_file = client.call(JobStatus(id=job[0].id, wait=True))

if extracted_file.status == "SUCCESS":
    result = client.call(RetrieveStorageObject(extracted_file.result))
    print(result)
