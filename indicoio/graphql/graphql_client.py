import logging
from indicoio.client import RequestProxy
from indicoio.errors import IndicoRequestError

logger = logging.getLogger(__file__)


class GraphClient(RequestProxy):
    def gql_query(self, query: str) -> dict:
        """
        Base GraphQL query method
        """
        response = self.post("/graph/api/graphql", json={"query": query})
        errors = response.pop("errors", [])
        if errors:
            extras = {"locations": [error.pop("locations") for error in errors]}
            raise IndicoRequestError(
                error="\n".join(error["message"] for error in errors),
                code=400,
                extras=extras,
            )
        return response

    def inspect_schema(self, type_name):
        return self.gql_query(
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

