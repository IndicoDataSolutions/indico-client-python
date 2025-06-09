from typing import TYPE_CHECKING, List

from indico.client.request import GraphQLRequest, PagedRequestV2
from indico.types.component_blueprint import BlueprintPage, BlueprintTags

if TYPE_CHECKING:  # pragma: no cover
    from typing import Any, Optional

    from indico.typing import Payload


class ListGallery(PagedRequestV2[BlueprintPage]):
    """
    List all blueprints available in the gallery.

    Args:
        filter (GenericScalar): filters to apply to the blueprints
        limit (int): maximum number of blueprints to return
        order_by (str): order to sort the blueprints by
        desc (bool): whether to sort the blueprints in descending order
        cursor (str): cursor to start the pagination from
    """

    query = """
        query getGalleryBlueprints($asc: Boolean, $cursor: String, $sortBy: String, $size: Int, $filters: GenericScalar) {
            gallery {
                component {
                    blueprintsPage(
                        asc: $asc
                        cursor: $cursor
                        filter: $filters
                        size: $size
                        sortBy: $sortBy
                    ) {
                        componentBlueprints {
                            id
                            name
                            componentType
                            icon
                            description
                            enabled
                            footer
                            tags
                            modelOptions
                        }
                        cursor
                        total
                    }
                }
            }
        }
    """

    def __init__(
        self,
        filters: "Optional[str]" = None,
        limit: int = 100,
        order_by: str = "name",
        desc: bool = False,
        cursor: "Optional[str]" = None,
        **kwargs: "Any",
    ):
        super().__init__(
            self.query,
            variables={
                "filters": filters,
                "size": limit,
                "sortBy": order_by,
                "asc": not desc,
                "cursor": cursor,
                **kwargs,
            },
        )

    def process_response(self, response: "Payload") -> "BlueprintPage":
        response = super().parse_payload(
            response, nested_keys=["gallery", "component", "blueprintsPage"]
        )
        return BlueprintPage(
            blueprints=[
                component
                for component in response["gallery"]["component"]["blueprintsPage"][
                    "componentBlueprints"
                ]
            ]
        )


class GetGalleryTags(GraphQLRequest[BlueprintTags]):
    """
    List all blueprint tags available in the gallery.

    Args:
        component_family (str): the family of components to filter by
        tag_categories (str): the category(ies) of tags to filter by
    """

    query = """
        query getGalleryBlueprints($componentFamily: ComponentFamily, $tagCategories: [BPTagCategory]) {
            gallery {
                component {
                    availableTags(componentFamily: $componentFamily, tagCategories: $tagCategories) {
                        tag
                        value
                        tagCategory
                    }
                }
            }
        }
    """

    def __init__(
        self,
        component_family: "Optional[str]" = None,
        tag_categories: "Optional[List[str]]" = None,
    ):
        self.component_family = component_family
        self.tag_categories = tag_categories
        super().__init__(
            self.query,
            variables={
                "componentFamily": component_family,
                "tagCategories": tag_categories,
            },
        )

    def process_response(self, response: "Payload") -> "BlueprintTags":
        return BlueprintTags(
            tags=[
                tag
                for tag in super().parse_payload(response)["gallery"]["component"][
                    "availableTags"
                ]
            ]
        )
