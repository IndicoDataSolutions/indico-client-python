from typing import Tuple
from indico.client import IndicoClient
from indico.queries import DeleteWorkflowComponent, GetWorkflow, GetDataset
from indico.types import ModelGroup, ModelTaskType, NewLabelsetArguments

from ..data.datasets import *  # noqa


def test_add_mg_new_labelset(indico, org_annotate_dataset):
    client = IndicoClient()
    workflowreq = CreateWorkflow(
        dataset_id=org_annotate_dataset.id, name=f"OrgAnnotate-test-{int(time.time())}"
    )
    wf = client.call(workflowreq)
    mg_name = f"TestAnnotationModelGroup-{int(time.time())}"
    labelset_name = "test-create-labelset"
    after_component_id = wf.component_by_type("INPUT_OCR_EXTRACTION").id
    source_column_id = org_annotate_dataset.datacolumn_by_name(
        "News Headlines w/Company Names"
    ).id
    modelgroupreq = AddModelGroupComponent(
        name=mg_name,
        dataset_id=org_annotate_dataset.id,
        workflow_id=wf.id,
        after_component_id=after_component_id,
        source_column_id=source_column_id,
        new_labelset_args=NewLabelsetArguments(
            name=labelset_name,
            task_type=ModelTaskType.ANNOTATION,
            target_names=["target 1", "target 2"],
            datacolumn_id=source_column_id,
        ),
    )

    wf = client.call(modelgroupreq)
    dataset = client.call(GetDataset(id=org_annotate_dataset.id))
    assert dataset.labelset_by_name(labelset_name)


def test_delete_workflow_component(
    indico, airlines_dataset, airlines_workflow, airlines_model_group: ModelGroup
):
    client = IndicoClient()
    # get workflow that includes mg component
    wf = client.call(GetWorkflow(workflow_id=airlines_workflow.id))
    num_components = len(wf.components)
    num_links = len(wf.component_links)
    mg_comp_id = next(c.id for c in wf.components if c.component_type == "MODEL_GROUP")
    wf = client.call(
        DeleteWorkflowComponent(
            workflow_id=airlines_workflow.id, component_id=mg_comp_id
        )
    )
    assert len(wf.components) == num_components - 1
    assert mg_comp_id not in {c.id for c in wf.components}
    assert len(wf.component_links) == num_links - 1
