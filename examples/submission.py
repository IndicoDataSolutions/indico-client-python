from indico import IndicoClient, IndicoConfig
from indico.queries import CreateSubmissionResult, WorkflowSubmission, JobStatus


# Create an Indico API client
config = IndicoConfig(''
    host="app.indico.io", api_token_path="./path/to/indico_api_token.txt"
)
client = IndicoClient(config=config)

# Create a new Submission using a previously created workflow
workflow_id = 5
job = client.call(
    WorkflowSubmission(
        workflow_id=workflow_id, files=["./path_to_doc.pdf"], submission=True
    )
)
submission_id = client.call(JobStatus(id=job[0].id, wait=True)).result['submission_ids'][0]

# Create a Submission result, and download the result file
result_url = client.call(
    CreateSubmissionResult(
        submission_id=submission_id, wait=True
    )
)
result = client.call(RetrieveStorageObject(result_url))