from indico import IndicoClient
from indico.queries import (
    JobStatus,
    ListWorkflows,
    RetrieveStorageObject,
    WorkflowSubmission,
)

# Use your dataset's id to call it's associated workflow
dataset_id = 6826

client = IndicoClient()

# Return a list of workflows for this dataset id or an empty list if there are none
workflows = client.call(ListWorkflows(dataset_ids=[dataset_id]))

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
