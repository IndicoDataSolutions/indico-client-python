import os

from indico.client import IndicoClient
from indico.queries import (
    AddExchangeIntegration,
    StartIntegration,
    DeleteIntegration,
    PauseIntegration,
)

from indico.types import Workflow, Integration, ModelGroup
from tests.integration.data.datasets import (
    airlines_workflow,
    airlines_dataset,
    org_annotate_workflow,
    org_annotate_dataset,
    org_annotate_exchange_integration,
    org_annotate_model_group,
    exchange_integration_to_delete,
    started_exchange_integration
)

def test_add_integration(airlines_workflow: Workflow):
    client = IndicoClient()
    creds = {
        "clientId": os.getenv("EXCH_CLIENT_ID"),
        "clientSecret": os.getenv("EXCH_CLIENT_SECRET"),
        "tenantId": os.getenv("EXCH_TENANT_ID"),
    }

    config = {"userId": os.getenv("EXCH_USER_ID"), "folderId": "mailFolders('inbox')"}

    integ: Integration = client.call(
        AddExchangeIntegration(
            workflow_id=airlines_workflow.id, config=config, credentials=creds
        )
    )

    assert integ.workflow_id == airlines_workflow.id
    assert integ.config.folder_name == "Inbox"


def test_start_integration(
    org_annotate_exchange_integration: Integration,
    org_annotate_model_group: ModelGroup,
    org_annotate_workflow: Workflow,
):
    integ = org_annotate_exchange_integration
    assert not integ.enabled
    client = IndicoClient()
    resp = client.call(
        StartIntegration(
            integration_id=integ.id
        )
    )
    assert resp["startWorkflowIntegration"]["success"]
    

def test_delete_integration(exchange_integration_to_delete: Integration):
    integ = exchange_integration_to_delete
    client = IndicoClient()
    resp = client.call(
        DeleteIntegration(
            integration_id=integ.id
        )
    )
    assert resp["deleteWorkflowIntegration"]["success"]


def test_pause_integration(started_exchange_integration: Integration):
    integ = started_exchange_integration
    client = IndicoClient()
    resp = client.call(
        PauseIntegration(
            integration_id=integ.id
        )
    )
    assert resp["pauseWorkflowIntegration"]["success"]
