from indicoio.client import IndicoClient


class GraphClient(IndicoClient):
    def graphql(self, query):
        return self.post("/graph/api/graphql", json={"query": query})

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

