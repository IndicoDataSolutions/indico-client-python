from typing import TYPE_CHECKING

from indico.client.request import GraphQLRequest

if TYPE_CHECKING:  # pragma: no cover
    from indico.typing import Payload


class GetIPAVersion(GraphQLRequest[str]):
    query = """
        "query getIPAVersion {
            ipaVersion
        }
    """

    def __init__(self) -> None:
        super().__init__(self.query)

    def process_response(self, response: "Payload") -> str:
        version: str = super().parse_payload(response)["ipaVersion"]
        return version
