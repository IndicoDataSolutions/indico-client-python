import logging
from indicoio.client import RequestProxy
from indicoio.errors import IndicoRequestError

logger = logging.getLogger(__file__)


class GraphClient(RequestProxy):
    def query(self, query: str, variables=None) -> dict:
        """
        Base GraphQL query method
        """
        response = self.post(
            "/graph/api/graphql", json={"query": query, "variables": variables}
        )
        errors = response.pop("errors", [])
        if errors:
            extras = {"locations": [error.pop("locations") for error in errors]}
            raise IndicoRequestError(
                error="\n".join(error["message"] for error in errors),
                code=400,
                extras=extras,
            )
        return response

    def inspect_schema(self, type_name: str=None):
        if type_name:
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
        else:
            return self.query(
                """
                query IntrospectionQuery {
                    __schema {
                        queryType {
                        name
                        }
                        mutationType {
                        name
                        }
                        subscriptionType {
                        name
                        }
                        types {
                        ...FullType
                        }
                        directives {
                        name
                        description
                        locations
                        args {
                            ...InputValue
                        }
                        }
                    }
                    }

                    fragment FullType on __Type {
                    kind
                    name
                    description
                    fields(includeDeprecated: true) {
                        name
                        description
                        args {
                        ...InputValue
                        }
                        type {
                        ...TypeRef
                        }
                        isDeprecated
                        deprecationReason
                    }
                    inputFields {
                        ...InputValue
                    }
                    interfaces {
                        ...TypeRef
                    }
                    enumValues(includeDeprecated: true) {
                        name
                        description
                        isDeprecated
                        deprecationReason
                    }
                    possibleTypes {
                        ...TypeRef
                    }
                    }

                    fragment InputValue on __InputValue {
                    name
                    description
                    type {
                        ...TypeRef
                    }
                    defaultValue
                    }

                    fragment TypeRef on __Type {
                    kind
                    name
                    ofType {
                        kind
                        name
                        ofType {
                        kind
                        name
                        ofType {
                            kind
                            name
                            ofType {
                            kind
                            name
                            ofType {
                                kind
                                name
                                ofType {
                                kind
                                name
                                ofType {
                                    kind
                                    name
                                }
                                }
                            }
                            }
                        }
                        }
                    }
                }
                """
            )

