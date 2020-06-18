import os
from indico import IndicoClient, IndicoConfig
from indico.queries import ListWorkflowsForDataset, WorkflowSubmission, JobStatus, RetrieveStorageObject


host = "app"
user = "beta"
domain = "indico.io"
home = os.environ["HOME"]
token_path = f"{home}/indico/tokens/{host}-{user}/indico_api_token.txt"
dataset_id = 6826

my_config = IndicoConfig(
    host=f"{host}.{domain}", api_token_path=token_path
)

client = IndicoClient(config=my_config)

# List workflows for this datasets and call the first one
w = client.call(ListWorkflowsForDataset(dataset_id=dataset_id))
if len(w) > 0:    
    print(f"{w[0].id} - {w[0].name}")

    job = client.call(WorkflowSubmission(
        files=["./try-it-out-sample1.pdf"],
        workflow_id=w[0].id
    ))

    print(f"Workflow Job ID = {job.id}")

    # Retrieve and print your workflow results
    status = client.call(JobStatus(id=job.id, wait=True))

    wf_result = client.call(RetrieveStorageObject(status.result))

    print(wf_result)
