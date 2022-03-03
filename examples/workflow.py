from indico import IndicoClient, IndicoConfig
from indico.queries import (
    JobStatus,
    RetrieveStorageObject,
    WorkflowSubmission, CreateWorkflow, GetDataset, ListWorkflows, AddModelGroupComponent,
)

# Use your dataset's id to call its associated workflow
dataset_id = 6826
workflow_name = "Test Workflow"
# the name of the datacolumn in your dataset
datacolumn = "column_name"
# name of an existing labelset.
labelset_name = "labelset_name"

my_config = IndicoConfig(
    host="app.indico.io", api_token_path="./path/to/indico_api_token.txt"
)
client = IndicoClient(config=my_config)

dataset = client.call(GetDataset(id=dataset_id))

# Example 1: Create a new workflow and model on an existing dataset.
# create a new workflow
new_workflow = client.call(CreateWorkflow(name=workflow_name, dataset_id=dataset_id))

# First, find the component you want this model to follow after.
# A component is essentially a step in the workflow process.
# in this case, we want it after OCR.
after_component_id = new_workflow.component_by_type("INPUT_OCR_EXTRACTION").id

# now, create the request with your parameters.
modelgroupreq = AddModelGroupComponent(
    name=workflow_name,
    dataset_id=dataset.id,
    after_component_id=after_component_id,
    source_column_id=dataset.datacolumn_by_name(datacolumn).id,
    labelset_column_id=dataset.labelset_by_name(labelset_name).id,
    workflow_id=new_workflow.id
)

client.call(modelgroupreq)

# Example 2: Simple submission.

# Return a list of workflows for this dataset id or an empty list if there are none
workflows = client.call(ListWorkflows(dataset_ids=[dataset_id]))

# You can run this with the newly created workflow or with an existing one.
if workflows:
    # Send a document through the workflow
    # Get back one Job per file
    jobs = client.call(
        WorkflowSubmission(
            workflow_id=workflows[0].id,
            files=["./path/to/sample.pdf"],
            submission=False,
        )
    )
    job = jobs[0]

    # Retrieve and print your result
    status = client.call(JobStatus(id=job.id, wait=True))
    wf_result = client.call(RetrieveStorageObject(status.result))
    print(wf_result)

else:
    print("You don't have any workflows for this dataset")
