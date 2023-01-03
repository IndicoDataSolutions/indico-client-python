from datetime import datetime
from enum import Enum
from indico.types import BaseType

class ExchangeIntegrationCredentials(BaseType):
    client_id: str
    client_secret: str
    tenant_id: str

class ExchangeIntegrationConfiguration(BaseType):
    user_id: str
    folder_id: str
    folder_name: str
    filters: str

class IntegrationType(Enum):
    EXCHANGE = 1

class Integration(BaseType):

    id: int
    workflow_id: int
    enabled: bool
    config: ExchangeIntegrationConfiguration
    created_at: datetime
    integration_type: IntegrationType