from indicoio.graphql import GraphClient
from .base import ObjectProxy


class Indico(ObjectProxy):
    def __init__(self, config_options=None):
        self.request_client = GraphClient(config_options)

    def model_groups(self, *fields):
        """
        Schema Introspection Client method generation should take care of query building
        and response extraction
        """
        fields = fields or ("id", "name")
        model_groups_response = self.request_client.gql_query(
            f"""query {{
        modelGroups {{
            modelGroups {{
                {",".join(fields)}
            }}
        }}}}"""
        )

        return model_groups_response["data"]["modelGroups"]["modelGroups"]
