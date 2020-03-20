# -*- coding: utf-8 -*-

from indico.client.request import GraphQLRequest, RequestChain
from indico.types.jobs import Job


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

    JobStatus is used to either wait for completion or query the status of an asynchronous
    job in the Indico Platform.
    
    Args:
        id (int): id of the job to query for status.
        wait (bool): Wait for the job to complete? Default is True
    
    Returns:
        Job: With the job result available in a result attribute. Note that the result
        will often be JSON but can also be a dict with the URL of a StorageObject on
        the Indico Platform. 
    """

    previous: Job = None
    def __init__(self, id: str, wait: bool=True):
        self.id = id
        self.wait = wait

    def requests(self):
        yield _JobStatus(id=self.id)
        if self.wait:
            # Check status of job until done if wait == True
            while (not (self.previous.status in ["SUCCESS"] and self.previous.ready == True) 
                or self.previous.status in ["FAILURE", "REJECTED", "REVOKED", "IGNORED", "RETRY"]):
                yield _JobStatus(id=self.id)
            yield _JobStatusWithResult(id=self.id)