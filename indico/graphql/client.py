import logging
from indico.http.client import RequestProxy
from indico.errors import IndicoRequestError
from typings import Dict, Any
logger = logging.getLogger(__file__)


class GraphClient(RequestProxy):
    def query(self, query: str, variables: Dict[str, Any]=None) -> dict:
        """
        Base GraphQL query method
        """
        response = self.post("/graph/api/graphql", json={"query": query, "variables": variables})
        errors = response.pop("errors", [])
        if errors:
            extras = {"locations": [error.pop("locations") for error in errors]}
            raise IndicoRequestError(
                error="\n".join(error["message"] for error in errors),
                code=400,
                extras=extras,
            )
        return response

    def inspect_schema(self, type_name: str): 
        return self.query(
            f"""query {{
            __type(name: "{type_name}") {{
                name
                fields {{
                    name
                    type {{
                        name
                        kind
                    }}
                }}
            }}
        }}
        """
        )

