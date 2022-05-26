from typing import Dict, List, Union

from indico.client.request import GraphQLRequest, RequestChain, PagedRequest
from indico.filters import ExampleFilter
from indico.types import Example, model_group


class ListModelGroupExamples(PagedRequest):
    """
    List all examples associated with a given model group ID.
    Supports pagination (limit becomes page_size)

    Options:
        model_group_ids (List[int]): Model group ids to filter by
        filters (ExampleFilter or Dict): Submission attributes to filter by
        limit (int, default=1000): Maximum number of Submissions to return
        orderBy (str, default="ID"): Submission attribute to filter by
        desc: (bool, default=True): List in descending order

    Returns:
        List[Example]: All the found Example objects
        If paginated, yields results one at a time
    """

    query = """
        query GetExamples($modelGroupId:Int, $orderBy: ExampleOrder, $desc: Boolean, $limit: Int, $filters: ExampleFilter, $after: Int, $before: Int) {
            modelGroups(modelGroupIds: [$modelGroupId]) {
                modelGroups {
                    pagedExamples(orderBy:$orderBy, desc:$desc, limit: $limit, filters: $filters, after: $after, before: $before) {
                        examples {
                            id
                            status
                            datafileId
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
        model_group_id: int = None,
        filters: Union[Dict, ExampleFilter] = None,
        limit: int = 1000,
        order_by: str = "ID",
        desc: bool = True,
        after: int = None,
        before: int = None,
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

    def process_response(self, response) -> List[Example]:
        response = response["data"]["modelGroups"]["modelGroups"][0]
        _pg = next(iter(response.values()))["pageInfo"]
        self.has_next_page = _pg["hasNextPage"]
        self.variables["after"] = _pg["endCursor"] if self.has_next_page else None
        return [Example(**s) for s in response["pagedExamples"]["examples"]]
