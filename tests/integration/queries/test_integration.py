import os

from indico.client import IndicoClient
from indico.queries import AddExchangeIntegration
from indico.types import Workflow, Integration
from ..data.datasets import airlines_workflow, airlines_dataset

def test_add_exchange_integration(airlines_workflow: Workflow):
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

    int: Integration = client.call(
        AddExchangeIntegration(
            workflow_id=airlines_workflow.id,
            config=config,
            credentials=creds
        )
    )
    
    assert int.workflow_id == airlines_workflow.id
    assert int.config.folder_name == "Inbox"