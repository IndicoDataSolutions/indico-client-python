import typing as t

from indico import GraphQLRequest
from indico.errors import IndicoInputError
from indico.types.workflow import ComponentFamily
from indico.types.custom_blueprint import TaskBlueprint

SUPPORTED_CUSTOM_COMPONENT_FAMILIES = [
    ComponentFamily.OUTPUT,
    ComponentFamily.FILTER,
    ComponentFamily.MODEL,
]


class RegisterCustomBlueprint(GraphQLRequest):
    """
    Mutation to register a custom blueprint, making it available in the gallery to add to workflows

    Args:
        component_family (ComponentFamily): family this blueprint belongs to; supported families are Output, Filter, and Model
        name (str): Name of the blueprint
        description (str): Description of this blueprint
        config (dict): Blueprint configuration options
        tags: (list[str]): List of tags associated with this blueprint

    Options:
        footer (str): Footnote for this blueprint's description
        icon (str): Image to use when displaying this blueprint in the gallery. Can be the name of an Indico-provided image,
        or the storage location of a custom image. If left unspecified, the platform will use a default icon.
        all_access (bool): This blueprint can be added to all workflows
        dataset_ids (list[int]): This blueprint can only be added to workflows associated with these dataset ids

    Returns:
        TaskBlueprint: The newly created TaskBlueprint object
    """

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
        if (
            not component_family
            or not name
            or not description
            or not config
            or not tags
        ):
            none_vals = []
            if not component_family:
                none_vals.append("component_family")
            if not name:
                none_vals.append("name")
            if not description:
                none_vals.append("description")
            if not config:
                none_vals.append("config")
            if not tags:
                none_vals.append("tags")
            raise IndicoInputError(
                f"The following arguments cannot be None: {', '.join(none_vals)}"
            )
        if not all([isinstance(t, str) for t in tags]):
            raise IndicoInputError("'tags' must be a list of strings")
        if not all(config.values()):
            raise IndicoInputError("values in the 'config' dict must not be None")
        if not isinstance(component_family, ComponentFamily):
            raise IndicoInputError(
                "'component_family' must be of type indico.types.workflows.ComponentFamily"
            )
        if component_family not in SUPPORTED_CUSTOM_COMPONENT_FAMILIES:
            raise IndicoInputError(
                f"component_family must be one of {', '.join([cf.name for cf in SUPPORTED_CUSTOM_COMPONENT_FAMILIES])}"
            )

        comp_fam_str = component_family.name.title()
        self.mutation_name = f"createCustom{comp_fam_str}TaskBlueprint"
        super().__init__(
            self.query.format(
                config_type=f"{comp_fam_str}Config",
                mutation_name=self.mutation_name,
            ),
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
        return TaskBlueprint(**super().process_response(response)[self.mutation_name])
