# -*- coding: utf-8 -*-

from indico.types.base import BaseType, JSONType


class Job(BaseType):
    """
    An Asynchronous Job in the Indico Platform.

    Many operations like DocumentExtraction and ModelGroupPredict are handled in the
    Indico Platform via Jobs. When you make a DocumentExtraction call, you are queuing
    a job in the Platform and a Job object is returned by client.call(..)

    Attributes:
        id (int): job id
        status (str): "SUCCESS", "FAILURE", "REJECTED", "REVOKED", "IGNORED", "RETRY"
        ready (bool):
    """

    id: int
    status: str
    result: JSONType
    ready: bool

    def __init__(self, **kwargs):
        if "jobId" in kwargs:
            kwargs["id"] = kwargs["jobId"]
            del kwargs["jobId"]
        super().__init__(**kwargs)
