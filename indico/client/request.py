from abc import abstractmethod
from enum import Enum
from typing import TYPE_CHECKING, Generic, TypeVar, cast

from indico.errors import IndicoRequestError

if TYPE_CHECKING:  # pragma: no cover
    from typing import Any, Dict, Iterator, List, Optional, Union

    from indico.typing import AnyDict

ResponseType = TypeVar("ResponseType")


class HTTPMethod(Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"


class HTTPRequest(Generic[ResponseType]):
    def __init__(self, method: HTTPMethod, path: str, **kwargs: "Any"):
        self.method: HTTPMethod = method
        self.path: str = path
        self._kwargs: "AnyDict" = kwargs

    @property
    def kwargs(self) -> "AnyDict":
        return self._kwargs

    def process_response(self, response: "Any") -> "ResponseType":
        return cast("ResponseType", response)


class GraphQLRequest(Generic[ResponseType], HTTPRequest[ResponseType]):
    def __init__(self, query: str, variables: "Optional[AnyDict]" = None):
        self.query: str = query
        self.variables: "Optional[AnyDict]" = variables

        super().__init__(HTTPMethod.POST, "/graph/api/graphql")

    @property
    def kwargs(self) -> "AnyDict":
        return {"json": {"query": self.query, "variables": self.variables}}

    def parse_payload(self, response: "AnyDict") -> "Any":
        raw_response: "AnyDict" = cast("AnyDict", super().process_response(response))
        errors: "List[AnyDict]" = raw_response.pop("errors", [])

        if errors:
            extras: "Dict[str, List[Any]]" = {
                "locations": [error.pop("locations", None) for error in errors]
            }

            raise IndicoRequestError(
                error="\n".join(error["message"] for error in errors),
                code=400,
                extras=extras,
            )

        return raw_response["data"]

    def process_response(self, response: "AnyDict") -> "ResponseType":
        raw_response = self.parse_payload(response)
        # technically incorrect, but necessary for backwards compatibility
        return cast("ResponseType", raw_response)


class PagedRequest(GraphQLRequest[ResponseType]):
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

    def parse_payload(self, response: "AnyDict") -> "Any":
        raw_response: "AnyDict" = cast("AnyDict", super().parse_payload(response))

        _pg = next(iter(raw_response.values())).get("pageInfo")
        if not _pg:
            raise ValueError("The supplied GraphQL must include 'pageInfo'.")

        self.has_next_page = _pg["hasNextPage"]
        cast("AnyDict", self.variables)["after"] = (
            _pg["endCursor"] if self.has_next_page else None
        )

        return raw_response


class RequestChain(Generic[ResponseType]):
    previous: "Any" = None
    result: "Optional[ResponseType]" = None

    @abstractmethod
    def requests(
        self,
    ) -> "Iterator[Union[RequestChain[Any], HTTPRequest[Any], Delay]]":
        raise NotImplementedError(
            "RequestChains must define an iterator for their requests;"
            "otherwise, subclass GraphQLResponse instead."
        )


class Delay:
    def __init__(self, seconds: "Union[int, float]" = 2):
        self.seconds = seconds
