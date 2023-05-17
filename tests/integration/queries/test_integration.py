import os
from time import sleep

from indico.client import IndicoClient
from indico.queries import AddExchangeIntegration, StartIntegration, GetWorkflow
from indico.types import Workflow, Integration, ModelGroup
from tests.integration.data.datasets import airlines_workflow, airlines_dataset, org_annotate_workflow, org_annotate_dataset, org_annotate_exchange_integration, org_annotate_model_group

def test_add_integration(airlines_workflow: Workflow):
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
            workflow_id=airlines_workflow.id,
            config=config,
            credentials=creds
        )
    )
    
    assert integ.workflow_id == airlines_workflow.id
    assert integ.config.folder_name == "Inbox"


def test_start_integration(org_annotate_exchange_integration: Integration, org_annotate_model_group: ModelGroup, org_annotate_workflow: Workflow):
    integ = org_annotate_exchange_integration
    assert not integ.enabled
    client = IndicoClient()
    resp = client.call(
        StartIntegration(
            integration_id=integ.id
        )
    )
    assert resp["startWorkflowIntegration"]["success"]