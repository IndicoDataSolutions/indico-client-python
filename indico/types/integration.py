from datetime import datetime
from enum import Enum

from indico.types import BaseType


class IntegrationType(Enum):
    EXCHANGE = 1


class ExchangeIntegrationCredentials(BaseType):
    """
    Credentials needed to connect a Microsoft Exchange server to an Indico workflow using
    """

    client_id: str
    client_secret: str
    tenant_id: str


class ExchangeIntegrationConfiguration(BaseType):
    """
    Configuration options available for an integration with Microsoft Exchange
    """

    user_id: str
    folder_id: str
    folder_name: str
    filters: str


class Integration(BaseType):
    """
    An integration pulls document from a third-party data source and submits them to a workflow

    Args:
        id(int): ID of the integration
        workflow_id(int): ID of the workflow to submit to.
        enabled(bool): Whether Indico is currently sending documents from this datasource to the workflow.
        created_at(datetime): When this integration was created.
        integration_type(IntegrationType): Type of the data source for this integration
    """

    id: int
    workflow_id: int
    enabled: bool
    created_at: datetime
    integration_type: IntegrationType


class ExchangeIntegration(Integration):
    config: ExchangeIntegrationConfiguration
