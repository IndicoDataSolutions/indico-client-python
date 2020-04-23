from typing import Dict, Any
from enum import Enum
from indico.errors import IndicoRequestError
import time


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
            extras = {"locations": [error.pop("locations") for error in errors]}
            raise IndicoRequestError(
                error="\n".join(error["message"] for error in errors),
                code=400,
                extras=extras,
            )
        return response["data"]


class RequestChain:
    previous: Any = None
    result: Any = None

    def requests(self):
        pass


class Debouncer:
    def __init__(self):
        self.timeout = 0
        self.max_timeout = 5

    def backoff(self):
        self.increment_timeout()
        time.sleep(self.timeout)

    def increment_timeout(self):
        if self.timeout < self.max_timeout:
            self.timeout += 1
