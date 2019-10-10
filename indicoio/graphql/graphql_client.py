import logging
from indicoio.client import IndicoClient
from indicoio.errors import IndicoRequestError

logger = logging.getLogger(__file__)


class GraphClient(IndicoClient):
    def graphql(self, query: str) -> dict:
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

    def inspect(self, type_name):
        return self.graphql(
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

