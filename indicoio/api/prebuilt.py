import json
from .indico import Indico
from .job_result import JobResult

from indicoio.preprocess.pdf import pdf_preprocess
from indicoio.errors import IndicoInputError
from indicoio.client.storage import StorageClient
from pathlib import Path
from typing import List, Union


def _convert_options_to_str(options):
    return ",".join(f"{key}: {json.dumps(option)}" for key, option in options.items())


class IndicoApi(Indico):
    """
    IndicoApi

    Example::

        api_client = IndicoApi()
        api_client.pdf_extraction(["url or file"], **options)

    """

    def pdf_extraction(
        self, data: List[str], job_results: bool = False, **pdf_extract_options
    ):
        """
        Extracts and returns the contents of a PDF Document

        :param data: List of inputs for extraction.
        :param job_results: True to return the id of the prediction job rather than the prediction results directly.
        :pdf_extract_options: Options to pass to PDF extraction
        """
        if not isinstance(data, list):
            raise IndicoInputError(
                "This function expects a list input. If you have a single piece of data, please wrap it in a list"
            )
        data = [pdf_preprocess(datum) for datum in data]
        data = json.dumps(data)

        option_string = _convert_options_to_str(pdf_extract_options)

        response = self.graphql.query(
            f"""
            mutation {{
                pdfExtraction(data: {data}, {option_string}) {{
                    jobId
                }}
            }}
        """
        )

        job_id = response["data"]["pdfExtraction"]["jobId"]
        job = self.build_object(JobResult, id=job_id)
        if job_results:
            return job
        else:
            job.wait()
            return job.result()

    def document_extraction(
        self, data: List, job_results: bool = False, json_config=None
    ):
        """
        Extracts and returns the contents of a Word Document

        :param data: List of inputs for extraction. Can be list of file paths or list of byte arrays.
        :param job_results: True to return the id of the prediction job rather than the prediction results directly.
        :document_extraction_options: Options to pass to Document extraction
        """
        if not isinstance(data, list):
            data = [data]

        if not json_config:
            json_config = {"preset_config": "simple"}

        file_inputs = self.storage.upload(data)

        variables = {"files": file_inputs, "jsonConfig": json.dumps(json_config)}

        response = self.graphql.query(
            f"""
            mutation($files: [FileInput], $jsonConfig: JSONString) {{
                documentExtraction(files: $files, jsonConfig: $jsonConfig ) {{
                    jobIds
                }}
            }}
            """,
            variables=json.dumps(variables),
        )

        job_ids = response["data"]["documentExtraction"]["jobIds"]
        jobs = [self.build_object(JobResult, id=job_id) for job_id in job_ids]

        if job_results:
            return jobs
        else:
            extracted = []
            for job in jobs:
                job.wait()
                url = job.result()
                downloaded = self.storage.download(url)
                extracted.append(downloaded)
            return extracted
