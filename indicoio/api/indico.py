from .base import ObjectProxy
from .model_group import ModelGroup


class Indico(ObjectProxy):
    def model_groups(self, *fields):
        """
        Schema Introspection Client method generation should take care of query building
        and response extraction
        """
        fields = fields or ("id", "name", "status", "retrainRequired")
        model_groups_response = self.graphql.query(
            f"""query {{
        modelGroups {{
            modelGroups {{
                {",".join(fields)}
            }}
        }}}}"""
        )

        return [
            self.build_object(ModelGroup, **mg)
            for mg in model_groups_response["data"]["modelGroups"]["modelGroups"]
        ]
