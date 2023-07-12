import typing as t

from indico import GraphQLRequest
from indico.types.workflow import ComponentFamily
from indico.types.custom_blueprint import TaskBlueprint

class RegisterCustomBlueprint(GraphQLRequest):
    query = """
mutation createCustomBP(
  $name: String!,
  $description: String!,
  $footer: String!,
  $tags: [BlueprintTag]!,
  $config: {config_type}!,
  $icon: String,
  $allAccess: Boolean,
  $datasetIds: [Int]
) {{
  {mutation_name}(
    name: $name,
    description: $description,
    footer: $footer,
    tags: $tags,
    config: $config,
    icon: $icon,
    allAccess: $allAccess,
    datasetIds: $datasetIds
  ) {{
    id
    name
    componentFamily
    icon
    description
    footer
    tags
    enabled
    config
  }}
}}
"""

    def __init__(
        self,
        component_family: ComponentFamily,
        name: str,
        description: str,
        config: t.Dict,
        tags: t.List[str],
        footer: str = "",
        icon: str = None,
        all_access: bool = None,
        dataset_ids: t.List[int] = None,
    ):
        comp_fam_str = component_family.name.title()
        self.mutation_name = f"createCustom{comp_fam_str}TaskBlueprint"
        super().__init__(
            self.query.format(config_type = f"{comp_fam_str}Config", mutation_name=self.mutation_name, ),
            variables={
                "name": name,
                "description": description,
                "footer": footer,
                "config": config,
                "tags": tags,
                "icon": icon,
                "allAccess": all_access,
                "datasetIds": dataset_ids,
            },
        )

    def process_response(self, response) -> TaskBlueprint:
        return TaskBlueprint(
            **super().process_response(response)[self.mutation_name]
        )

