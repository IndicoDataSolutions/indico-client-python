"""
Main Indico IPA Client
"""
import json
import time
from typing import Union, List, Dict, Any
from pathlib import Path

from .base import ObjectProxy
from .model_group import ModelGroup
from .job_result import JobResult
from indicoio.errors import IndicoRequestError
from indicoio.graphql.queries import (
    DATASET_UPLOAD_STATUS,
    CREATE_DATASET_MUTATION,
    FINISH_DATASET_PIPELINE,
    DATASET_STATUS,
    CREATE_MODEL_GROUP,
)


class Indico(ObjectProxy):
    def model_groups(self, *fields):
        """
        Schema Introspection Client method generation should take care of query building
        and response extraction
        """
        fields = fields or ("id", "name", "status", "retrainRequired")
        model_groups_response = self.graphql.query(
            f"""query {{
        modelGroups {{
            modelGroups {{
                {",".join(fields)}
            }}
        }}}}"""
        )

        return [
            self.build_object(ModelGroup, **mg)
            for mg in model_groups_response["data"]["modelGroups"]["modelGroups"]
        ]

    def create_model_group(
        self,
        name: str,
        dataset_id: int,
        source_column_id: int,
        labelset_column_id: int,
        label_resolution: str,
        processors: List[Dict[str, Any]] = None,
    ):
        return self.graphql.query(
            query=CREATE_MODEL_GROUP,
            variables={
                "datasetId": dataset_id,
                "interlabelerResolution": label_resolution,
                "labelsetColumnId": labelset_column_id,
                "name": name,
                "sourceColumnId": source_column_id,
                "processors": processors or [],
            },
        )

    def create_dataset(self, name: str, data: List[Union[str, Path]], ocr: bool = True):
        files = self.storage.upload(data)
        response = self.graphql.query(
            query=CREATE_DATASET_MUTATION, variables={"metadata": json.dumps(files)}
        )
        dataset_id = response["data"]["newDataset"]["id"]
        files_status = ["DOWNLOADING"]
        interval = 1
        while any(status == "DOWNLOADING" for status in files_status):
            status_response = self.graphql.query(
                variables={"id": dataset_id}, query=DATASET_UPLOAD_STATUS
            )
            files_status = [
                file_info["status"]
                for file_info in status_response["data"]["dataset"]["files"]
            ]

            interval = max(interval * 2, interval)
            time.sleep(interval)

        if any(status != "DOWNLOADED" for status in files_status):
            files = status_response["data"]["dataset"]["files"]
            file = next(file for file in files if file["status"] != "DOWNLOADED")
            raise IndicoRequestError(f"{file['name']} failed to be processed.")

        result = self.graphql.query(
            query=FINISH_DATASET_PIPELINE,
            variables={"datasetId": dataset_id, "name": name, "ocr": ocr},
        )
        status = result["data"]["processDataset"]["status"]
        while status == "CREATING":
            status = self.graphql.query(
                query=DATASET_STATUS, variables={"id": dataset_id}
            )["data"]["dataset"]["status"]
        # TODO: Dataset DataObject
        return dataset_id

    def submission(self, workflow_id: int, data: List[Union[str, Path]]):
        """
        Submission API
        workflow_id: ID of workflow to run
        data: List of string or read file-like objects
        """
        jobs = []
        storage_obj_dicts = self.storage.upload(data)
        for storage_obj in storage_obj_dicts:
            response = self.graphql.query(
                """mutation workflowSubmissionMutation($workflowId: Int!, $files: [FileInput]!) {
                    workflowSubmission(workflowId: $workflowId, files: $files) {
                        jobId
                    }
                }""",
                variables={"workflowId": workflow_id, "files": [storage_obj]},
            )
            job_id = response["data"]["workflowSubmission"]["jobId"]
            job = self.build_object(JobResult, id=job_id)
            jobs.append(job)
        return jobs

