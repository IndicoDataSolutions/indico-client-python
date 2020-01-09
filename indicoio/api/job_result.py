from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import json

from .base import ObjectProxy

max_interval = 10

WAIT_POOL = ThreadPoolExecutor(10)


def await_job_results(job_results):
    job_results = list(job_results)
    futures = {}
    for idx, job_result in enumerate(job_results):
        futures[WAIT_POOL.submit(job_result.wait)] = idx

    for future in as_completed(futures):
        idx = futures[future]
        yield idx, job_results[idx].result()


class JobResult(ObjectProxy):
    def wait(self, interval=1):
        response = self.graphql.query(
            f"""query {{
                        job(id: "{self["id"]}") {{
                            ready
                            status
                        }}
                }}"""
        )
        self.update(response["data"]["job"])

        if self.get("ready", False) is not True:
            time.sleep(interval)
            self.wait(interval=interval + 1)

    def status(self):
        response = self.graphql.query(
            f"""query {{
                    job(id: "{self["id"]}") {{
                        status
                    }}
            }}"""
        )
        self["status"] = response["data"]["job"]["status"]
        return self["status"]

    def ready(self):
        response = self.graphql.query(
            f"""query {{
                        job(id: "{self["id"]}") {{
                            ready
                        }}
                }}"""
        )
        self.update(response["data"]["job"])

        return self.get("ready", False) is True

    def result(self):
        if self.get("result") is not None:
            return self["result"]

        response = self.graphql.query(
            f"""query {{
                    job(id: "{self["id"]}") {{
                        status
                        result
                    }}
            }}"""
        )
        job = response["data"]["job"]
        self.update(job)
        self["result"] = json.loads(self["result"])
        return self["result"]
