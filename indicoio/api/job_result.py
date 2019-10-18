import json

from .base import ObjectProxy


class JobResult(ObjectProxy):
    def wait(self):
        while self.get("ready", False):
            response = self.graphql.query(
                f"""query {{
                        job(id: "{self["id"]}") {{
                            ready
                            status
                        }}
                }}"""
            )

            self.update(response["data"]["job"])

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
