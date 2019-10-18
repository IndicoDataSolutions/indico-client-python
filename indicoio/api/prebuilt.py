import json
from .indico import Indico
from .job_result import JobResult

from indicoio.preprocess.pdf import pdf_preprocess
from indicoio.errors import IndicoInputError


class IndicoApi(Indico):
    def pdf_extraction(self, data, job_results=False, **pdf_extract_options):
        if not isinstance(data, list):
            raise IndicoInputError(
                "This function expects a list input. If you have a single piece of data, please wrap it in a list"
            )
        data = [pdf_preprocess(datum) for datum in data]
        data = json.dumps(data)
        option_string = ",".join(
            f"{key}: {json.dumps(option)}"
            for key, option in pdf_extract_options.items()
        )
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
