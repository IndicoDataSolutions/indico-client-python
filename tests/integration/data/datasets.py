import os
import pytest
import time
from pathlib import Path
from indico.client import IndicoClient
from indico.queries import (
    CreateDataset, 
    CreateWorkflow, 
    AddModelGroupComponent, 
    GetModelGroup, 
    AddExchangeIntegration, 
    GetWorkflow,
)
from indico.queries.workflow_components import _AddWorkflowComponent
from indico.types import ModelGroup, Dataset, Workflow, Integration

PUBLIC_URL = "https://github.com/IndicoDataSolutions/indico-client-python/raw/master/tests/integration/data/"


@pytest.fixture(scope="module")
def airlines_dataset(indico):
    client = IndicoClient()
    dataset_filepath = str(Path(__file__).parents[0]) + "/AirlineComplaints.csv"

    response = client.call(
        CreateDataset(
            name=f"AirlineComplaints-test-{int(time.time())}", files=[dataset_filepath]
        )
    )
    assert response.status == "COMPLETE"
    return response


@pytest.fixture(scope="module")
def airlines_workflow(indico, airlines_dataset: Dataset):
    client = IndicoClient()
    workflowreq = CreateWorkflow(dataset_id=airlines_dataset.id, name=f"AirlineComplaints-test-{int(time.time())}")
    wf = client.call(workflowreq)
    # add default output node
    client.call(_AddWorkflowComponent(after_component_id=wf.component_by_type("OUTPUT_JSON_FORMATTER").id,
        component="{\"component_type\":\"default_output\",\"config\":{}}",
        workflow_id=wf.id,
        after_component_link=None
    ))
    response = client.call(GetWorkflow(workflow_id=wf.id))

    return response


@pytest.fixture(scope="module")
def too_small_dataset(indico):
    client = IndicoClient()
    dataset_filepath = str(Path(__file__).parents[0]) + "/TooSmall.csv"

    response = client.call(
        CreateDataset(
            name=f"TooSmall-test-{int(time.time())}", files=[dataset_filepath]
        )
    )
    assert response.status == "COMPLETE"
    return response

@pytest.fixture(scope="module")
def too_small_workflow(indico, too_small_dataset: Dataset) -> Workflow:
    client = IndicoClient()
    workflowreq = CreateWorkflow(dataset_id=too_small_dataset.id, name=f"TooSmall-test-{int(time.time())}")
    wf = client.call(workflowreq)
    # add default output node
    client.call(_AddWorkflowComponent(after_component_id=wf.component_by_type("OUTPUT_JSON_FORMATTER").id,
        component="{\"component_type\":\"default_output\",\"config\":{}}",
        workflow_id=wf.id,
        after_component_link=None
    ))
    response = client.call(GetWorkflow(workflow_id=wf.id))

    return response


@pytest.fixture(scope="module")
def airlines_model_group(indico, airlines_dataset: Dataset, airlines_workflow: Workflow) -> ModelGroup:
    client = IndicoClient()
    name = f"TestCreateModelGroup-{int(time.time())}"
    after_component_id = airlines_workflow.component_by_type("INPUT_OCR_EXTRACTION").id
    modelgroupreq = AddModelGroupComponent(
        name=name,
        dataset_id=airlines_dataset.id,
        after_component_id=after_component_id,
        source_column_id=airlines_dataset.datacolumn_by_name("Text").id,
        labelset_column_id=airlines_dataset.labelset_by_name("Target_1").id,
        workflow_id=airlines_workflow.id
    )

    workflow_update: Workflow = client.call(modelgroupreq)
    component = workflow_update.model_group_by_name(name)

    mg = client.call(GetModelGroup(id=component.model_group.id, wait=True))

    return mg


@pytest.fixture(scope="module")
def cats_dogs_image_dataset(indico):
    client = IndicoClient()
    dataset_filepath = str(Path(__file__).parents[0]) + "/dog_vs_cats_small.csv"

    response = client.call(
        CreateDataset(
            name=f"DogsAndCats-test-{int(time.time())}",
            files=dataset_filepath,
            from_local_images=True,
        )
    )
    assert response.status == "COMPLETE"
    return response


@pytest.fixture(scope="module")
def cats_dogs_image_workflow(indico, cats_dogs_image_dataset: Dataset):
    client = IndicoClient()
    workflowreq = CreateWorkflow(dataset_id=cats_dogs_image_dataset.id, name=f"DogsAndCats-test-{int(time.time())}")
    response = client.call(workflowreq)

    return response


@pytest.fixture(scope="module")
def cats_dogs_modelgroup(indico, cats_dogs_image_dataset: Dataset, cats_dogs_image_workflow) -> ModelGroup:
    client = IndicoClient()
    name = f"TestCreateObjectDetectionMg-{int(time.time())}"

    model_training_options = {
        "max_iter": 20,
        "lr": 0.1,
        "batch_size": 1,
        "filter_empty": False,
        "test_size": 0.2,
        "use_small_model": True,
    }
    after_component_id = airlines_workflow.component_by_type("INPUT_OCR_EXTRACTION").id
    modelgroupreq = AddModelGroupComponent(
        name=name,
        dataset_id=airlines_dataset.id,
        after_component_id=after_component_id,
        source_column_id=airlines_dataset.datacolumn_by_name("urls").id,
        labelset_column_id=airlines_dataset.labelset_by_name("label").id,
        workflow_id=airlines_workflow.id,
        model_training_options=model_training_options
    )

    workflow_update: Workflow = client.call(modelgroupreq)
    component = workflow_update.model_group_by_name(name)
    mg = client.call(GetModelGroup(id=component.model_group.id, wait=True))

    return mg


@pytest.fixture(scope="module")
def org_annotate_dataset(indico):
    client = IndicoClient()
    dataset_filepath = str(Path(__file__).parents[0]) + "/org-annotate-labeled.csv"

    response = client.call(
        CreateDataset(
            name=f"OrgAnnotate-test-{int(time.time())}", files=[dataset_filepath]
        )
    )
    assert response.status == "COMPLETE"
    return response


@pytest.fixture(scope="module")
def org_annotate_workflow(indico, org_annotate_dataset: Dataset):
    client = IndicoClient()
    workflowreq = CreateWorkflow(dataset_id=org_annotate_dataset.id, name=f"OrgAnnotate-test-{int(time.time())}")
    wf = client.call(workflowreq)
    # add default output node
    client.call(_AddWorkflowComponent(after_component_id=wf.component_by_type("OUTPUT_JSON_FORMATTER").id,
        component="{\"component_type\":\"default_output\",\"config\":{}}",
        workflow_id=wf.id,
        after_component_link=None
    ))
    response = client.call(GetWorkflow(workflow_id=wf.id))
    return response


@pytest.fixture(scope="module")
def org_annotate_model_group(indico, org_annotate_dataset: Dataset, org_annotate_workflow: Workflow) -> ModelGroup:
    client = IndicoClient()
    name = f"TestFinetuneModelGroup-{int(time.time())}"
    after_component_id = org_annotate_workflow.component_by_type("INPUT_OCR_EXTRACTION").id
    modelgroupreq = AddModelGroupComponent(
        name=name,
        dataset_id=org_annotate_dataset.id,
        after_component_id=after_component_id,
        source_column_id=org_annotate_dataset.datacolumn_by_name("News Headlines w/Company Names").id,
        labelset_column_id=org_annotate_dataset.labelset_by_name("question_825").id,
        workflow_id=org_annotate_workflow.id
    )

    workflow_update: Workflow = client.call(modelgroupreq)
    component = workflow_update.model_group_by_name(name)

    mg = client.call(GetModelGroup(id=component.model_group.id, wait=True))

    return mg

@pytest.fixture(scope="module")
def org_annotate_exchange_integration(org_annotate_workflow: Workflow) -> Integration:
    client = IndicoClient()
    creds = {
        "clientId": os.getenv("EXCH_CLIENT_ID"),
        "clientSecret": os.getenv("EXCH_CLIENT_SECRET"),
        "tenantId": os.getenv("EXCH_TENANT_ID")
    }

    config = {
        "userId": os.getenv("EXCH_USER_ID"),
        "folderId": "mailFolders('inbox')"
    }

    integ: Integration = client.call(
        AddExchangeIntegration(
            workflow_id=org_annotate_workflow.id,
            config=config,
            credentials=creds
        )
    )

    return integ


@pytest.fixture(scope="module")
def exchange_integration_to_delete(org_annotate_workflow: Workflow) -> Integration:
    client = IndicoClient()
    creds = {
        "clientId": os.getenv("EXCH_CLIENT_ID"),
        "clientSecret": os.getenv("EXCH_CLIENT_SECRET"),
        "tenantId": os.getenv("EXCH_TENANT_ID")
    }

    config = {
        "userId": os.getenv("EXCH_USER_ID"),
        "folderId": "mailFolders('inbox')"
    }

    integ: Integration = client.call(
        AddExchangeIntegration(
            workflow_id=org_annotate_workflow.id,
            config=config,
            credentials=creds
        )
    )

    return integ