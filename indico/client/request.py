from typing import Dict, Any
from enum import Enum
from indico.errors import IndicoRequestError

class HTTPMethod(Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"

class HTTPRequest:
    def __init__(self, method: HTTPMethod, path: str, data: Dict[str, Any]=None):
        self.method = method
        self.path = path
        self.data = data

    def process_response(self, response):
        return response

class GraphQLRequest(HTTPRequest):
    def __init__(self, query: str, variables: Dict[str, Any]):
        self.query = query
        self.variables = variables
        self.method = HTTPMethod.POST
        self.path = "/graph/api/graphql"

    @property
    def data(self):
        return {
            "query": self.query, 
            "variables": self.variables
        }

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
        return response