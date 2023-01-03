import jsons
from typing import List

from indico import GraphQLRequest, RequestChain
from indico.errors import IndicoInputError
from indico.types.integration import Integration, ExchangeIntegrationConfiguration, ExchangeIntegrationCredentials

class AddExchangeIntegration(GraphQLRequest):
    """
    Mutation to add a Microsoft Exchange integration to a workflow

    Args:
        workflow_id(int): workflow to add integration to
        config(ExchangeIntegrationConfiguration): settings for which mailbox to point to and which emails to process
        credentials(ExchangeIntegrationCredentials): client id, client secret, and tenant id for authenticating with Exchange

    """

    query = """
    mutation addExchangeIntegration($workflow_id: Int!, $config: ExchangeIntegrationConfigurationInput!, $credentials: ExchangeIntegrationCredentialsInput!){
  addExchangeIntegrationToWorkflow(workflowId: $workflow_id, config: $config, credentials: $credentials){
    integration{
      id
      enabled
      workflowId
      createdAt
      config {
        filters
        userId
        folderName
        folderId
      }
    }
  }
}
    """

    def __init__(
        self,
        config: ExchangeIntegrationConfiguration,
        credentials: ExchangeIntegrationCredentials,
        workflow_id: int,
    ):
        super().__init__(
            self.query,
            variables={
                "config": config,
                "credentials": credentials,
                "workflow_id": workflow_id,
            },
        )

    def process_response(self, response) -> Integration:
        return Integration(
            **super().process_response(response)["addExchangeIntegrationToWorkflow"]["integration"]
        )