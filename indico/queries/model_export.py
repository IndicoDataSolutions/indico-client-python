from indico.client.request import Delay, GraphQLRequest, RequestChain
from indico.types.model_export import ModelExport


class _CreateModelExport(GraphQLRequest):
    query = """
        mutation ($modelId: Int!) {
            createModelExport(
                modelId: $modelId
            ) {
                id
                name
                status
                modelId
            }
        }
    """

    def __init__(self, model_id: int):
        self.model_id = model_id
        super().__init__(self.query, variables={"modelId": model_id})

    def process_response(self, response) -> ModelExport:
        return ModelExport(**super().process_response(response)["createModelExport"])


class CreateModelExport(RequestChain):
    """
    Create a model export.

    Available on 6.14+ only.
    """

    previous: ModelExport | None = None

    def __init__(
        self,
        model_id: int,
        wait: bool = True,
        request_interval: int | float = 5,
    ):
        self.wait = wait
        self.model_id = model_id
        self.request_interval = request_interval
        super().__init__()

    def requests(self):
        yield _CreateModelExport(self.model_id)
        if self.wait:
            while self.previous and self.previous.status not in ["COMPLETE", "FAILED"]:
                yield GetModelExports([self.previous.id])
                self.previous = self.previous[0]
                yield Delay(seconds=self.request_interval)

        yield GetModelExports([self.previous.id], with_signed_url=self.wait is True)


class GetModelExports(GraphQLRequest):
    """
    Get model export(s).

    Available on 6.14+ only.
    """

    query = """
        query getModelExports($exportIds: [Int]) {
            modelExports(exportIds: $exportIds) {
                modelExports {
                    {fields}
                }
            }
        }
    """

    _base_fields = [
        "id",
        "name",
        "status",
        "modelId",
        "filePath",
        "createdAt",
        "createdBy",
    ]

    def __init__(self, export_ids: list[int], with_signed_url: bool = False):
        if with_signed_url:
            self._base_fields.append("signedUrl")

        query_with_fields = self.query.replace("{fields}", "\n".join(self._base_fields))
        super().__init__(query_with_fields, variables={"exportIds": export_ids})

    def process_response(self, response) -> list[ModelExport]:
        return [
            ModelExport(**export)
            for export in super().process_response(response)["modelExports"][
                "modelExports"
            ]
        ]
