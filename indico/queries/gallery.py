from typing import TYPE_CHECKING, Optional, cast

from indico.client.request import GraphQLRequest, PagedRequest
from indico.types.component_blueprint import BlueprintPage, BlueprintTags

if TYPE_CHECKING:  # pragma: no cover
    from typing import Any, List

    from indico.filters import ComponentBlueprintFilter
    from indico.typing import AnyDict, Payload


class ListGallery(PagedRequest[BlueprintPage]):
    """
    List all blueprints available in the gallery.

    Args:
        filters (ComponentBlueprintFilter): filters to apply to the blueprints
        limit (int): maximum number of blueprints to return
        order_by (str): order to sort the blueprints by
        desc (bool): whether to sort the blueprints in descending order
    """

    query = """
        query getGalleryBlueprints($desc: Boolean, $orderBy: COMPONENTBLUEPRINT_COLUMN_ENUM, $skip: Int, $limit: Int, $after: Int, $before: Int, $filters: ComponentBlueprintFilter) {
            gallery {
                component {
                    blueprintsPage(
                        skip: $skip
                        before: $before
                        after: $after
                        limit: $limit
                        desc: $desc
                        orderBy: $orderBy
                        filters: $filters
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
                        pageInfo {
                            startCursor
                            endCursor
                            hasNextPage
                            aggregateCount
                        }
                    }
                }
            }
        }
    """

    def __init__(
        self,
        filters: "Optional[ComponentBlueprintFilter]" = None,
        limit: int = 100,
        order_by: str = "ID",
        desc: bool = False,
        **kwargs: "Any",
    ):
        super().__init__(
            self.query,
            variables={
                "filters": filters,
                "limit": limit,
                "orderBy": order_by,
                "desc": desc,
                **kwargs,
            },
        )

    def process_response(
        self, response: "Payload", _: "Optional[List[str]]" = None
    ) -> "BlueprintPage":
        response = super().process_response(
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
    """

    query = """
        query getGalleryBlueprints($componentFamily: ComponentFamily) {
            gallery {
                component {
                    availableTags(componentFamily: $componentFamily) {
                        tag
                        value
                    }
                }
            }
        }
    """

    def __init__(self, component_family: "Optional[str]" = None):
        self.component_family = component_family
        super().__init__(
            self.query,
            variables={"componentFamily": component_family},
        )

    def process_response(self, response: "Payload") -> "BlueprintTags":
        response = cast(Payload, super().process_response(response))
        return BlueprintTags(
            tags=[tag for tag in response["gallery"]["component"]["availableTags"]]
        )
