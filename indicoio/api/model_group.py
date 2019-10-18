"""
TODO: Move predict to selected_model.predict. Create Model and auto fetch selected_model on ModelGroup to get Model

"""
import time
import json

from .base import ObjectProxy
from .job_result import JobResult
from indicoio.errors import IndicoInputError


class ModelGroup(ObjectProxy):
    def predict(self, data, model_id=None, job_results=False, **predict_kwargs):
        if not isinstance(data, list):
            raise IndicoInputError(
                "This function expects a list input. If you have a single piece of data, please wrap it in a list"
            )

        data = json.dumps(data)

        if not model_id:
            model_id = self.get_selected_model()["id"]

        response = self.graphql.query(
            f"""mutation {{
            modelPredict(modelId: {model_id}, data: {data}) {{
                jobId
            }}
        }}"""
        )
        job_id = response["data"]["modelPredict"]["jobId"]
        job = self.build_object(JobResult, id=job_id)
        if job_results:
            return job
        else:
            job.wait()
            return job.result()

    def load(self, model_id=None):
        if self.info().get("load_status") == "ready":
            return "ready"

        if not model_id:
            model_id = self.get_selected_model()["id"]

        response = self.graphql.query(
            f"""mutation {{
            modelLoad(modelId: {model_id}) {{
                status
            }}
        }}"""
        )

        status = response["data"]["modelLoad"]["status"]

        while status == "loading":
            status = self.info().get("load_status", "loading")
            time.sleep(1)

        return status

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
        return {}

    def get_selected_model(self):
        response = self.graphql.query(
            f"""query {{
                modelGroups(modelGroupIds: [{self["id"]}]) {{
                    modelGroups {{
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
        return self["selectedModel"]

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
