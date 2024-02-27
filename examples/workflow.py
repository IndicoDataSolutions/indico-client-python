from indico import IndicoClient, IndicoConfig
from indico.queries import (
    JobStatus,
    RetrieveStorageObject,
    WorkflowSubmission,
    CreateWorkflow,
    GetDataset,
    ListWorkflows,
    AddModelGroupComponent,
    GetWorkflow,
    AddLinkedLabelComponent,
    AddLinkClassificationComponent,
)
from indico.types import (
    NewLabelsetArguments,
    ModelTaskType,
    LinkedLabelGroup,
    LinkedLabelStrategy,
)

# Use your dataset's id to call its associated workflow
dataset_id = 6826
workflow_name = "Test Workflow"
# the name of the datacolumn in your dataset
datacolumn = "column_name"
# name of an existing labelset.
labelset_name = "labelset_name"

my_config = IndicoConfig(
    host="try.indico.io", api_token_path="./path/to/indico_api_token.txt"
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
    workflow_id=new_workflow.id,
)

client.call(modelgroupreq)


# Example 2: Simple submission.

# Send a document through the workflow
# Get back one submission ID per file (List[int])
submission_id = client.call(
    WorkflowSubmission(
        workflow_id=new_workflow.id,  # REPLACE with your [int] workflow ID- can also be found in the UI
        files=["./path/to/sample.pdf"],
    )
)
job = client.call(SubmissionResult(submission_id[0], wait=True))
wf_result = client.call(RetrieveStorageObject(job.result))


# Example 3 - Adding additional components.

# Example 3a: Adding a model group component with a new labelset.
workflow_id = 1234
dataset_id = 4567
dataset = client.call(GetDataset(id=dataset_id))

workflow = client.call(GetWorkflow(workflow_id=workflow_id))

after = workflow.component_by_type("INPUT_OCR_EXTRACTION")

new_labelset = NewLabelsetArguments(
    name="extraction-sample-labelset",
    datacolumn_id=dataset.datacolumn_by_name(datacolumn).id,
    task_type=ModelTaskType.FORM_EXTRACTION,
    target_names=["one", "two", "three"],
)
add_extraction = AddModelGroupComponent(
    workflow_id=workflow.id,
    name="extraction-sample",
    dataset_id=dataset_id,
    source_column_id=dataset.datacolumn_by_name(datacolumn).id,
    after_component_id=after.id,
    new_labelset_args=new_labelset,
)
updated_workflow = client.call(add_extraction)

# Example 3b: Adding a linked label component. May only be added after an extraction model.
workflow_id = 1234
dataset_id = 4567

dataset = client.call(GetDataset(id=dataset_id))

workflow = client.call(GetWorkflow(workflow_id=workflow_id))

extraction_model = workflow.model_group_by_name("your-extraction-model-name")

add_groups = LinkedLabelGroup(
    name="group_1",
    strategy=LinkedLabelStrategy.BY_KEY,
    class_ids=[1, 2],
    strategy_settings={"key_classes": ["1"]},
)

add_linked_label_transformer = AddLinkedLabelComponent(
    workflow_id=workflow.id,
    after_component_id=after.id,
    model_group_id=extraction_model.model_group.id,
    labelset_id=dataset.labelset_by_name(labelset_name).id,
    groups=[add_groups],
)
updated = client.call(add_linked_label_transformer)

# Example 3c: Adding a link classification component with filtered classes
workflow_id = 1234
dataset_id = 4567

dataset = client.call(GetDataset(id=dataset_id))

workflow = client.call(GetWorkflow(workflow_id=workflow_id))

model = workflow.model_group_by_name("your--model-name")

add_classes_filter = AddLinkClassificationComponent(
    workflow_id=workflow.id,
    after_component_id=after.id,
    model_group_id=model.model_group.id,
    filtered_classes=[["class"]],
    labels="actual",
)
updated = client.call(add_classes_filter)
