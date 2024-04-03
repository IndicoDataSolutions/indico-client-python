from abc import ABC, abstractmethod
from enum import Enum
from typing import TYPE_CHECKING, Generic, TypeVar, cast

from indico.errors import IndicoRequestError
from indico.typing import AnyDict

if TYPE_CHECKING:  # pragma: no cover
    from typing import Any, Dict, Iterator, List, Optional, Union

# the generic vars effectively disregarded through explicit casting throughout
# this file in order to support better user-facing typing via client.call and
# actual gql response types
ProvidedResponseType = TypeVar("ProvidedResponseType")
ProcessedResponseType = TypeVar("ProcessedResponseType")
RequestClass = TypeVar("RequestClass")
FinalResponseType = TypeVar("FinalResponseType")


class HTTPMethod(Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"


class HTTPRequest(Generic[ProvidedResponseType, ProcessedResponseType]):
    def __init__(self, method: HTTPMethod, path: str, **kwargs: "Any"):
        self.method: HTTPMethod = method
        self.path: str = path
        self._kwargs: "AnyDict" = kwargs

    @property
    def kwargs(self) -> "AnyDict":
        return self._kwargs

    def process_response(
        self, response: "ProvidedResponseType"
    ) -> "ProcessedResponseType":
        return cast("ProcessedResponseType", response)


class GraphQLRequest(HTTPRequest[AnyDict, ProcessedResponseType]):
    def __init__(self, query: str, variables: "Optional[AnyDict]" = None):
        self.query: str = query
        self.variables: "Optional[AnyDict]" = variables

        super().__init__(HTTPMethod.POST, "/graph/api/graphql")

    @property
    def kwargs(self) -> "AnyDict":
        return {"json": {"query": self.query, "variables": self.variables}}

    def process_response(self, response: "AnyDict") -> "ProcessedResponseType":
        raw_response: "AnyDict" = cast("AnyDict", super().process_response(response))
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

        return cast("ProcessedResponseType", raw_response["data"])


class PagedRequest(GraphQLRequest[ProcessedResponseType]):
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

    def process_response(self, response: "AnyDict") -> "ProcessedResponseType":
        raw_response = cast("AnyDict", super().process_response(response))

        _pg = next(iter(raw_response.values())).get("pageInfo")
        if not _pg:
            raise ValueError("The supplied GraphQL must include 'pageInfo'.")

        self.has_next_page = _pg["hasNextPage"]
        cast("AnyDict", self.variables)["after"] = (
            _pg["endCursor"] if self.has_next_page else None
        )
        return cast("ProcessedResponseType", raw_response)


class RequestChain(Generic[RequestClass, FinalResponseType], ABC):
    previous: "Any" = None
    result: "Optional[FinalResponseType]" = None

    @abstractmethod
    def requests(self) -> "Iterator[RequestClass]":
        ...


class Delay:
    def __init__(self, seconds: "Union[int, float]" = 2):
        self.seconds = seconds
