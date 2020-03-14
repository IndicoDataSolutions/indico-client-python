from time import sleep
from typing import List

from indico.client.request import GraphQLRequest, RequestChain
from indico.types.model_group import ModelGroup
from indico.types.jobs import Job

class GetModelGroup(GraphQLRequest):
    query = """
        query GetModelGroup($id: Int){
            modelGroups(modelGroupIds: [$id]) {
                    modelGroups {
                        id
                        name
                        status
                        selectedModel {
                            id
                            status
                        }
                    }
                }
            }
        """

    def __init__(self, id:int):
        super().__init__(query=self.query, variables={
            "id": id
        })

    def process_response(self, response):
        mg = ModelGroup(**super().process_response(response)["modelGroups"]["modelGroups"][0])
        return mg

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
                    name
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
                "labelsetColumnId": labelset_id
            }
        )

    def process_response(self, response):
        return ModelGroup(**super().process_response(response)["createModelGroup"])

class GetModelGroupSelectedModelStatus(GraphQLRequest):
    query = """
        query GetModelGroup($id: Int) {
                modelGroups(modelGroupIds: [$id]) {
                    modelGroups {
                        id
                        selectedModel {
                            id
                            status
                        }
                    }
                }
            }
        """

    def __init__(self, id:int):
        super().__init__(query=self.query, variables={
            "id": id
        })

    def process_response(self, response):
        mg = ModelGroup(**super().process_response(response)["modelGroups"]["modelGroups"][0])
        return mg.selected_model.status 


class CreateModelGroup(RequestChain):
    def __init__(
        self,
        name: str,
        dataset_id: int,
        source_column_id: int,
        labelset_id: int,
        wait: bool=False
    ):
        self.name = name
        self.dataset_id = dataset_id
        self.source_column_id = source_column_id
        self.labelset_id = labelset_id
        self.wait = wait

    def requests(self):
        yield _CreateModelGroup(
            name=self.name,
            dataset_id=self.dataset_id,
            source_column_id=self.source_column_id,
            labelset_id=self.labelset_id,
        )
        model_group_id = self.previous.id
        if self.wait:
            req =  GetModelGroupSelectedModelStatus(
                id = model_group_id
            )
            yield req
            while self.previous not in ["FAILED", "COMPLETE"]:
                sleep(1)
                yield req

            yield GetModelGroup(id=model_group_id)


class ModelGroupPredict(GraphQLRequest):
    query= """
        mutation ModelGroupPredict($modelId: Int, $data: [String]) {
            modelPredict(modelId: $modelId, data: $data) {{
                jobId
            }
        """
    def __init__(self, model_id: int, data: List[str]):
        super().__init__(query=self.query, variables={
            "modelId": model_id,
            "data": data
        })

    def process_response(self, response):
        return Job(**super().process_response(response)["modelPredict"])


