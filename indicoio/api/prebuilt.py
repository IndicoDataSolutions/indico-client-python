import json
from .indico import Indico
from .job_result import JobResult

from indicoio.preprocess.pdf import pdf_preprocess
from indicoio.errors import IndicoInputError
from typing import List


def _convert_options_to_str(options):
        return ",".join(
            f"{key}: {json.dumps(option)}"
            for key, option in options.items()
        )

class IndicoApi(Indico):
    def pdf_extraction(self, data: List[str], job_results: bool=False, **pdf_extract_options):
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

    def document_extraction(self, data: List[str], job_results: bool=False, **document_extraction_options):
        if not isinstance(data, list):
            raise IndicoInputError(
                "This function expects a list input. If you have a single piece of data, please wrap it in a list"
            )
        data = [pdf_preprocess(datum) for datum in data]
        data = json.dumps(data)

        option_string = _convert_options_to_str(options)
        
        response = self.graphql.query(
            f"""
            mutation {{
                documentExtraction(data: {data}, {option_string}) {{
                    jobId
                }}
            }}
            """
        )

        job_id = response["data"]["documentExtraction"]["jobId"]
        job = self.build_object(JobResult, id=job_id)
        if job_results:
            return job
        else:
            job.wait()
            return job.result()
