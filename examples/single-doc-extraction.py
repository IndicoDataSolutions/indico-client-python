from indico import IndicoClient
from indico.queries import DocumentExtraction, JobStatus, RetrieveStorageObject


# Create an Indico API client
client = IndicoClient()

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
