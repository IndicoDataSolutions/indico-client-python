# -*- coding: utf-8 -*-


from typing import Optional

from pydantic import Field

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

    id: int = Field(validation_alias="jobId")
    status: Optional[str] = None
    result: Optional[JSONType] = None
    ready: Optional[bool] = None
