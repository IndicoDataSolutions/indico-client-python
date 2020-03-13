from typing import List

from indico.client.request import GraphQLRequest, RequestChain
from indico.types.model_group import ModelGroup
from indico.types.jobs import Job

class _CreateModelGroup(GraphQLRequest):
    query = """
        mutation CreateModelGroup(
            $datasetId: Int!,
            $sourceColumnId: Int!,
            $labelsetColumnId: Int,
            $name: String!,
        ) {
                createModelGroup(
                    datasetId: $datasetId,
                    sourceColumnId: $sourceColumnId,
                    labelsetColumnId: $labelsetColumnId,
                    name: $name,
                ) {
                    id
                    status
                }
            }
    """

    def __init__(
        self,
        name: str,
        dataset_id: int,
        source_column_id: int,
        labelset_id: int,
    ):
        super().__init__(
            query=self.query,
            variables={
                "name": name,
                "datasetId": dataset_id,
                "sourceColumnId": source_column_id,
                "labelset_id": labelset_id
            }
        )

    def process_response(self, response):
        return ModelGroup(**super().process_response(response)["createModelGroup"])

class GetModelGroup(GraphQLRequest):
    query = """
        query GetModelGroup($id: Int) {
                modelGroups(modelGroupIds: [$id]) {
                    modelGroups {
                        id
                        name
                        status
                        selectedModel {
                            id
                        }
                    }
                }
            }
        """

    def __init__(self, id:int):
        super().__init__(query=self.query, variables={
            id: id
        })

    def process_response(self, response):
        return ModelGroup(**super().process_response(response)["modelGroups"]["modelGroups"])

class ModelGroupPredict(GraphQLRequest):
    query= """
        mutation ModelGroupPredict($modelId: Int, $data: [String]) {
            modelPredict(modelId: $modelId, data: $data) {{
                jobId
            }
        """
    def __init__(self, model_id: int, data: List(str)):
        super().__init__(query=self.query, variables={
            "modelId": model_id,
            "data": data
        })

    def process_response(self, response):
        return Job(**super().process_response(response)["modelPredict"])


