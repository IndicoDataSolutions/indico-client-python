import jsons
from indico.client import IndicoClient
from indico.queries import DeleteWorkflowComponent, GetWorkflow, GetDataset
from indico.queries.workflow_components import AddLinkClassificationComponent
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
            task_type=ModelTaskType.CLASSIFICATION_MULTIPLE,
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

def test_add_many_filtered_classes(indico, org_annotate_dataset):
    client = IndicoClient()
    workflowreq = CreateWorkflow(
        dataset_id=org_annotate_dataset.id, name=f"OrgAnnotate-test-{int(time.time())}"
    )
    wf = client.call(workflowreq)
    mg_name = f"TestAnnotationModelGroup-{int(time.time())}"
    labelset_name = "test-filtered-classes"
    after_component_id = next(c.id for c in wf.components if c.component_type == "INPUT_OCR_EXTRACTION")
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
            task_type=ModelTaskType.CLASSIFICATION_MULTIPLE,
            target_names=["type 1", "type 2", "type 3"],
            datacolumn_id=source_column_id,
        ),
    )
    wf = client.call(modelgroupreq)
    mg = next(c for c in wf.components if c.component_type == 'MODEL_GROUP')
    after_component_id = mg.id
    
    classes_to_filter = [
            ["type 1"],
            ["type 3"]
        ]
    filtered = AddLinkClassificationComponent(
            workflow_id=wf.id,
            after_component_id=after_component_id,
            model_group_id=mg.model_group.id,
            filtered_classes=classes_to_filter,
            labels="actual",
        )
    wf = client.call(filtered)
    new_component = next(c.id for c in wf.components if c.component_type == "LINK_CLASSIFICATION_MODEL")
    assert new_component is not None

def test_add_single_filtered_class(indico, org_annotate_dataset):
    client = IndicoClient()
    workflowreq = CreateWorkflow(
        dataset_id=org_annotate_dataset.id, name=f"OrgAnnotate-test-{int(time.time())}"
    )
    wf = client.call(workflowreq)
    mg_name = f"TestAnnotationModelGroup-{int(time.time())}"
    labelset_name = "test-filtered-classes"
    after_component_id = next(c.id for c in wf.components if c.component_type == "INPUT_OCR_EXTRACTION")
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
            task_type=ModelTaskType.CLASSIFICATION_MULTIPLE,
            target_names=["type 1", "type 2", "type 3"],
            datacolumn_id=source_column_id,
        ),
    )
    wf = client.call(modelgroupreq)
    mg = next(c for c in wf.components if c.component_type == 'MODEL_GROUP')
    after_component_id = mg.id
    
    classes_to_filter = [
            ["type 1"]
        ]
    filtered = AddLinkClassificationComponent(
            workflow_id=wf.id,
            after_component_id=after_component_id,
            model_group_id=mg.model_group.id,
            filtered_classes=classes_to_filter,
            labels="actual",
        )
    wf = client.call(filtered)
    new_component =  next(c.id for c in wf.components if c.component_type == 'LINK_CLASSIFICATION_MODEL')
    assert new_component is not None


def test_add_bad_syntax_filtered_classes(indico, org_annotate_dataset):
    client = IndicoClient()
    workflowreq = CreateWorkflow(
        dataset_id=org_annotate_dataset.id, name=f"OrgAnnotate-test-{int(time.time())}"
    )
    wf = client.call(workflowreq)
    mg_name = f"TestAnnotationModelGroup-{int(time.time())}"
    labelset_name = "test-filtered-classes"
    after_component_id = next(c.id for c in wf.components if c.component_type == "INPUT_OCR_EXTRACTION")
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
            task_type=ModelTaskType.CLASSIFICATION_MULTIPLE,
            target_names=["type 1", "type 2", "type 3"],
            datacolumn_id=source_column_id,
        ),
    )
    wf = client.call(modelgroupreq)
    mg = next(c for c in wf.components if c.component_type == 'MODEL_GROUP')
    after_component_id = mg.id
    
    classes_to_filter = [
            ["type 1"],
            ["type 2"]
        ]
    filtered = AddLinkClassificationComponent(
            workflow_id=wf.id,
            after_component_id=after_component_id,
            model_group_id=6108,
            filtered_classes=[classes_to_filter],
            labels="actual",
        )
    with pytest.raises(Exception):
        wf = client.call(filtered)
   