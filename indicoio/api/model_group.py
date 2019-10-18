import json

from .base import ObjectProxy
from .job_result import JobResult
from indicoio.errors import IndicoInputError


class ModelGroup(ObjectProxy):
    def info(self):
        response = self.graphql.query(
            f"""query {{
            modelGroupPredict(modelGroupId: {self["id"]}, data: {data}) {{
                jobId
            }}
        }}"""
        )

    def predict(self, data, job_results=False, **predict_kwargs):
        if not isinstance(data, list):
            raise IndicoInputError(
                "This function expects a list input. If you have a single piece of data, please wrap it in a list"
            )

        data = json.dumps(data)
        response = self.graphql.query(
            f"""mutation {{
            modelGroupPredict(modelGroupId: {self["id"]}, data: {data}) {{
                jobId
            }}
        }}"""
        )
        job_id = response["data"]["modelGroupPredict"]["jobId"]
        job = self.build_object(JobResult, id=job_id)
        if job_results:
            return job
        else:
            job.wait()
            return job.result()

    def info(self):
        response = self.graphql.query(
            f"""query {{
                modelGroups(modelGroupIds: [{self["id"]}]) {{
                    modelGroups {{
                        id
                        selectedModel {{
                            id
                            modelInfo
                        }}
                }}
            }}
        }}"""
        )

        model = response["data"]["modelGroups"]["modelGroups"][0]["selectedModel"]
        if model:
            return json.loads(model.get("modelInfo"))

    def refresh(self):
        response = self.graphql.query(
            f"""query {{
                modelGroups(modelGroupIds: [{self["id"]}]) {{
                    modelGroups {{
                        id
                        name
                        status
                        taskType
                        dataType
                        retrainRequired
                        labelset {{
                            id
                        }}
                        sourceColumn {{
                            id
                        }}
                        selectedModel {{
                            id
                            modelInfo
                        }}
                }}
            }}
        }}"""
        )
        mg = response["data"]["modelGroups"]["modelGroups"][0]
        self.update(mg)
