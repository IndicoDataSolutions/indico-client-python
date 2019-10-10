from indicoio.graphql import GraphClient


class Indico(GraphClient):
    def model_groups(self, *fields):
        """
        Schema Introspection Client method generation should take care of query building
        and response extraction
        """
        fields = fields or ("id", "name")
        model_groups_response = self.graphql(
            f"""query {{
        modelGroups {{
            modelGroups {{
                {",".join(fields)}
            }}
        }}}}"""
        )

        return model_groups_response["data"]["modelGroups"]["modelGroups"]
