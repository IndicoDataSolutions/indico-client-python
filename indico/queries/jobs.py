# -*- coding: utf-8 -*-
from typing import TYPE_CHECKING

from indico.client.request import Delay, GraphQLRequest, RequestChain
from indico.types.jobs import Job
from indico.types.utils import Timer

if TYPE_CHECKING:  # pragma: no cover
    from typing import Iterator, Optional, Union

    from indico.typing import Payload


class _JobStatus(GraphQLRequest["Job"]):
    query = """
        query JobStatus($id: String) {
            job(id: $id) {
                id
                ready
                status
            }
        }
    """

    def __init__(self, id: str):
        super().__init__(self.query, variables={"id": id})

    def process_response(self, response: "Payload") -> "Job":
        return Job(**super().parse_payload(response)["job"])


class _JobStatusWithResult(GraphQLRequest["Job"]):
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

    def __init__(self, id: str):
        super().__init__(self.query, variables={"id": id})

    def process_response(self, response: "Payload") -> "Job":
        return Job(**super().parse_payload(response)["job"])


class JobStatus(RequestChain["Job"]):
    """
    Status of a Job in the Indico Platform.

    JobStatus is used to either wait for completion or
    query the status of an asynchronous job in the Indico Platform.

    Args:
        id (int): ID of the job to query for status.
        wait (bool, optional): Whether to wait for the job to complete. Defaults to True.
        request_interval (int or float, optional): The maximum time in between retry calls when waiting. Defaults to 0.2.
        timeout (float or int, optional): Timeout after this many seconds.
            Ignored if not `wait`. Defaults to None.

    Returns:
        Job: With the job result available in a result attribute. Note that the result
        will often be JSON but can also be a dict with the URL of a StorageObject on
        the Indico Platform.

    Raises:
        IndicoTimeoutError: If `wait` is True, this error is raised if job has not
            completed after `timeout` seconds
    """

    previous: "Job"

    def __init__(
        self,
        id: str,
        wait: bool = True,
        request_interval: "Union[int, float]" = 0.2,
        timeout: "Optional[Union[int, float]]" = None,
    ):
        self.id = id
        self.wait = wait
        self.request_interval = request_interval
        self.timeout = timeout

    def requests(self) -> "Iterator[Union[_JobStatus, Delay, _JobStatusWithResult]]":
        yield _JobStatus(id=self.id)

        if self.wait:
            timer: "Optional[Timer]" = None
            if self.timeout is not None:
                timer = Timer(self.timeout)

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
                if timer:
                    timer.check()
                yield Delay(seconds=self.request_interval)
                yield _JobStatus(id=self.id)

            yield _JobStatusWithResult(id=self.id)
