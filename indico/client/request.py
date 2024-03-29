from enum import Enum
from typing import TYPE_CHECKING, cast

from indico.errors import IndicoInputError, IndicoRequestError

if TYPE_CHECKING:  # pragma: no cover
    from typing import Any, Dict, List, Optional, Union

    AnyDict = Dict[str, Any]


class HTTPMethod(Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"


class HTTPRequest:
    def __init__(self, method: HTTPMethod, path: str, **kwargs: "Any"):
        self.method: HTTPMethod = method
        self.path: str = path
        self._kwargs: "AnyDict" = kwargs

    @property
    def kwargs(self) -> "AnyDict":
        return self._kwargs

    def process_response(self, response: "AnyDict") -> "AnyDict":
        return response


class GraphQLRequest(HTTPRequest):
    def __init__(self, query: str, variables: "Optional[AnyDict]" = None):
        self.query: str = query
        self.variables: "Optional[AnyDict]" = variables

        super().__init__(HTTPMethod.POST, "/graph/api/graphql")

    @property
    def kwargs(self) -> "AnyDict":
        return {"json": {"query": self.query, "variables": self.variables}}

    def process_response(self, response: "AnyDict") -> "AnyDict":
        response = super().process_response(response)
        errors: "List[AnyDict]" = response.pop("errors", [])

        if errors:
            extras: "Dict[str, List[Any]]" = {
                "locations": [error.pop("locations", None) for error in errors]
            }

            raise IndicoRequestError(
                error="\n".join(error["message"] for error in errors),
                code=400,
                extras=extras,
            )

        return cast("AnyDict", response["data"])


class PagedRequest(GraphQLRequest):
    """
    To enable pagination, query must include $after as an argument
    and request pageInfo
        query Name(
            ...
            $after: Int
        ){
            items(
                ...
                after: $after
            ){
                items {...}
                pageInfo {
                    endCursor
                    hasNextPage
                }
            }
        }
    """

    def __init__(self, query: str, variables: "Optional[AnyDict]" = None):
        if variables is None:
            variables = {}

        variables["after"] = None
        self.has_next_page = True
        super().__init__(query, variables=variables)

    def process_response(
        self, response: "AnyDict", nested_keys: "Optional[List[str]]" = None
    ) -> "AnyDict":
        response = super().process_response(response)
        if nested_keys:
            _pg = response
            for key in nested_keys:
                if key not in _pg.keys():
                    raise IndicoInputError(
                        f"Nested key not found in response: {key}",
                    )
                _pg = _pg[key]
            _pg = _pg["pageInfo"]
        else:
            _pg = next(iter(response.values()))["pageInfo"]

        if not _pg:
            raise ValueError("The supplied GraphQL must include 'pageInfo'.")

        self.has_next_page = _pg["hasNextPage"]
        cast("AnyDict", self.variables)["after"] = (
            _pg["endCursor"] if self.has_next_page else None
        )
        return response


class RequestChain:
    previous: "Any" = None
    result: "Any" = None

    def requests(self) -> None:
        pass


class Delay:
    def __init__(self, seconds: "Union[int, float]" = 2):
        self.seconds = seconds
