from indico import IndicoClient, IndicoConfig
from indico.queries import ListWorkflowsForDataset, WorkflowSubmission, JobStatus, RetrieveStorageObject

# Use your dataset's id to call it's associated workflow
dataset_id = 6826

my_config = IndicoConfig(
    host="app.indico.io", api_token_path="./path/to/indico_api_token.txt"
)
client = IndicoClient(config=my_config)

# Return a list of workflows for this dataset id or an empty list if there are none
workflows = client.call(ListWorkflowsForDataset(dataset_id=dataset_id))

if workflows:
    # Send a document through the workflow
    job = client.call(
        WorkflowSubmission(files=["./path/to/sample.pdf"], workflow_id=workflows[0].id)
    )
    
    # Retrieve and print your result
    status = client.call(JobStatus(id=job.id, wait=True))
    wf_result = client.call(RetrieveStorageObject(status.result))
    print(wf_result)
    
else:
    print("You don't have any workflows for this dataset")