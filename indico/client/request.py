from enum import Enum
from typing import Any, Dict, Tuple

from indico.errors import IndicoRequestError


class HTTPMethod(Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"


class HTTPRequest:
    def __init__(self, method: HTTPMethod, path: str, **kwargs):
        self.method = method
        self.path = path
        self.kwargs = kwargs

    def process_response(self, response):
        return response


class GraphQLRequest(HTTPRequest):
    def __init__(self, query: str, variables: Dict[str, Any] = None):
        self.query = query
        self.variables = variables
        self.method = HTTPMethod.POST
        self.path = "/graph/api/graphql"

    @property
    def kwargs(self):
        return {"json": {"query": self.query, "variables": self.variables}}

    def process_response(self, response):
        response = super().process_response(response)
        errors = response.pop("errors", [])
        if errors:
            extras = {"locations": [error.pop("locations", None) for error in errors]}
            raise IndicoRequestError(
                error="\n".join(error["message"] for error in errors),
                code=400,
                extras=extras,
            )
        return response["data"]


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

    def __init__(self, query: str, variables: Dict[str, Any] = None):
        variables["after"] = None
        self.has_next_page = True
        super().__init__(query, variables=variables)

    def process_response(self, response):
        response = super().process_response(response)
        _pg = next(iter(response.values()))["pageInfo"]
        self.has_next_page = _pg["hasNextPage"]
        self.variables["after"] = _pg["endCursor"] if self.has_next_page else None
        return response


class RequestChain:
    previous: Any = None
    result: Any = None

    def requests(self):
        pass


class Debouncer:
    def __init__(self, max_timeout: Tuple[int, float] = 5):
        self.timeout = 0
        self.max_timeout = max_timeout or 5  # prevent None and 0

    def backoff(self) -> Tuple[int, float]:
        self.increment_timeout()
        return self.timeout

    def increment_timeout(self):
        if self.timeout < self.max_timeout:
            self.timeout += 1
