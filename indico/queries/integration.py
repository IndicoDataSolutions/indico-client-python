from typing import TYPE_CHECKING

from indico import GraphQLRequest
from indico.types.integration import ExchangeIntegration

if TYPE_CHECKING:  # pragma: no cover
    from indico.types.integration import (
        ExchangeIntegrationConfiguration,
        ExchangeIntegrationCredentials,
    )
    from indico.typing import AnyDict, Payload  # noqa: F401


class AddExchangeIntegration(GraphQLRequest["ExchangeIntegration"]):
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
        config: "ExchangeIntegrationConfiguration",
        credentials: "ExchangeIntegrationCredentials",
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

    def process_response(self, response: "Payload") -> "ExchangeIntegration":
        return ExchangeIntegration(
            **super().parse_payload(response)["addExchangeIntegrationToWorkflow"][
                "integration"
            ]
        )


class StartIntegration(GraphQLRequest["AnyDict"]):
    """
    Mutation to start an existing integration. Once an integration is started, documents will be submitted to the associated workflow.

    Args:
        integration_id(int): id of the integration to start

    """

    query = """
        mutation StartIntegration($integration_id: Int!){
          startWorkflowIntegration(integrationId: $integration_id){
            success
          }
        }
    """

    def __init__(
        self,
        integration_id: int,
    ):
        super().__init__(
            self.query,
            variables={"integration_id": integration_id},
        )


class DeleteIntegration(GraphQLRequest["AnyDict"]):
    """
    Mutation to delete an existing Integration.

    Args:
        integration_id(int): id of the integration to delete

    """

    query = """
        mutation DeleteWorkflowIntegration($integrationId: Int!) {
            deleteWorkflowIntegration(integrationId: $integrationId) {
                success
            }
        }
    """

    def __init__(self, integration_id: int):
        super().__init__(
            self.query,
            variables={"integrationId": integration_id},
        )


class PauseIntegration(GraphQLRequest["AnyDict"]):
    """
    Mutation to pause an existing Integration.

    Args:
        integration_id(int): id of the integration to pause
    """

    query = """
        mutation PauseIntegration($integrationId: Int!){
            pauseWorkflowIntegration(integrationId: $integrationId){
             success # bool
        }
    }
    """

    def __init__(self, integration_id: int):
        super().__init__(
            self.query,
            variables={"integrationId": integration_id},
        )
