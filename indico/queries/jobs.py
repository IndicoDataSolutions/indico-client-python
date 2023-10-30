# -*- coding: utf-8 -*-
import time

from indico.client.request import GraphQLRequest, RequestChain
from indico.types.jobs import Job
from indico.types.utils import Timer

class _JobStatus(GraphQLRequest):
    query = """
        query JobStatus($id: String) {
            job(id: $id) {
                id
                ready
                status
            }
        }
    """

    def __init__(self, id):
        super().__init__(self.query, variables={"id": id})

    def process_response(self, response):
        return Job(**super().process_response(response)["job"])


class _JobStatusWithResult(GraphQLRequest):
    query = """
        query JobStatus($id: String) {
            job(id: $id) {
                id
                ready
                status
                result
            }
        }
    """

    def __init__(self, id):
        super().__init__(self.query, variables={"id": id})

    def process_response(self, response):
        return Job(**super().process_response(response)["job"])


class JobStatus(RequestChain):
    """
    Status of a Job in the Indico Platform.

    JobStatus is used to either wait for completion or
    query the status of an asynchronous job in the Indico Platform.

    Args:
        id (int): id of the job to query for status.
        wait (bool, optional): Wait for the job to complete? Default is True
        timeout (int, optional): Timeout after this many seconds.
            Ignored if not `wait`. Defaults to None

    Returns:
        Job: With the job result available in a result attribute. Note that the result
        will often be JSON but can also be a dict with the URL of a StorageObject on
        the Indico Platform.

    Raises:
        IndicoTimeoutError: If `wait` is True, this error is raised if job has not
            completed after `timeout` seconds
    """

    previous: Job = None

    def __init__(self, id: str, wait: bool = True, request_interval=0.2, timeout=None):
        self.id = id
        self.wait = wait
        self.request_interval = request_interval
        self.timeout = timeout

    def requests(self):
        yield _JobStatus(id=self.id)
        if self.wait:
            if self.timeout is not None:
                timer = Timer(self.timeout)
                timer.run()
            # Check status of job until done if wait == True
            while not (
                (self.previous.status in ["SUCCESS"] and self.previous.ready)
                or self.previous.status
                in [
                    "FAILURE",
                    "REJECTED",
                    "REVOKED",
                    "IGNORED",
                    "RETRY",
                ]
            ):
                time.sleep(self.request_interval)
                yield _JobStatus(id=self.id)
            yield _JobStatusWithResult(id=self.id)
