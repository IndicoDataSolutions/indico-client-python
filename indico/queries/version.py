from typing import TYPE_CHECKING

from indico.client.request import GraphQLRequest

if TYPE_CHECKING:  # pragma: no cover
    from indico.typing import AnyDict


class GetIPAVersion(GraphQLRequest[str]):
    query = """
        "query getIPAVersion {
            ipaVersion
        }
    """

    def __init__(self):
        super().__init__(self.query)

    def process_response(self, response: "AnyDict") -> str:
        return response["ipaVersion"]
