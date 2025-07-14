from typing import TYPE_CHECKING

from indico.client.request import PagedRequest
from indico.filters import ModelGroupExampleFilter
from indico.types.questionnaire import Example

if TYPE_CHECKING:  # pragma: no cover
    from typing import List, Optional, Union

    from indico.typing import AnyDict, Payload


class ListModelGroupExamples(PagedRequest["List[Example]"]):
    """
    List all examples associated with a given model group ID.
    Supports pagination (limit becomes page_size)

    Options:
        model_group_ids (List[int]): Model group ids to filter by
        filters (ModelGroupExampleFilter or Dict): Example attributes to filter by
        limit (int, default=1000): Maximum number of Examples to return per page
        orderBy (str, default="ID"): Example attribute to filter by
        desc: (bool, default=True): List in descending order
        after (int): id to start the pagination from
        before (int): id to end the pagination at

    Returns:
        List[Example]: All the found Example objects
        If paginated, yields results one at a time
    """

    query = """
        query GetExamples($modelGroupId:Int, $orderBy: ExampleOrder, $desc: Boolean, $limit: Int, $filters: ExampleFilter, $after: Int, $before: Int) {
            modelGroups(modelGroupIds: [$modelGroupId]) {
                modelGroups {
                    pagedExamples(orderBy: $orderBy, desc: $desc, limit: $limit, filters: $filters, after: $after, before: $before) {
                        examples {
                            id
                            status
                            datafileIds
                            originalDatafileId
                            originalDatafileName
                        }
                        pageInfo {
                            startCursor
                            endCursor
                            hasNextPage
                        }
                    }
                }
            }
        }
    """

    def __init__(
        self,
        *,
        model_group_id: "Optional[int]" = None,
        filters: "Optional[Union[AnyDict, ModelGroupExampleFilter]]" = None,
        limit: int = 1000,
        order_by: str = "ID",
        desc: bool = True,
        after: "Optional[int]" = None,
        before: "Optional[int]" = None,
    ):
        variables = {
            "modelGroupId": model_group_id,
            "filters": filters,
            "limit": limit,
            "orderBy": order_by,
            "desc": desc,
            "after": after,
            "before": before,
        }
        super().__init__(
            self.query,
            variables=variables,
        )

    def process_response(self, response: "Payload") -> "List[Example]":
        example_page = super().parse_payload(
            response, nested_keys=["modelGroups", "modelGroups", 0, "pagedExamples"]
        )
        return [
            Example(**example)
            for example in example_page["modelGroups"]["modelGroups"][0][
                "pagedExamples"
            ]["examples"]
        ]
