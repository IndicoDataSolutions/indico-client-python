import time
import json

from .base import ObjectProxy

max_interval = 10


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
