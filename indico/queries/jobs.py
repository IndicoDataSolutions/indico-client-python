# -*- coding: utf-8 -*-
from typing import Tuple

from indico.client.request import Debouncer, GraphQLRequest, RequestChain
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
        id (int): ID of the job to query for status.
        wait (bool, optional): Whether to ait for the job to complete. Default is True
        timeout (float or int, optional): Timeout after this many seconds.
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

    def __init__(
        self,
        id: str,
        wait: bool = True,
        timeout: Tuple[int, float] = None,
        max_wait_time: Tuple[int, float] = 5,
    ):
        self.id = id
        self.wait = wait
        self.timeout = timeout
        self.max_wait_time = max_wait_time

    def requests(self):
        yield _JobStatus(id=self.id)
        if self.wait:
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
                if self.timeout is not None:
                    timer = Timer(self.timeout)
                    timer.check()
                yield Debouncer(max_timeout=self.max_wait_time)
                yield _JobStatus(id=self.id)
            yield _JobStatusWithResult(id=self.id)
