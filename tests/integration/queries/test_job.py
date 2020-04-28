from pathlib import Path

import pytest

from indico.client import IndicoClient
from indico.queries import JobStatus, DocumentExtraction
from indico.types.jobs import Job
from indico.errors import IndicoTimeoutError

def test_job_wait_on_success(indico):
    client = IndicoClient()
    dataset_filepath = str(Path(__file__).parents[1]) + "/data/mock.pdf"
    
    jobs = client.call(DocumentExtraction(files=[dataset_filepath], json_config='{"preset_config": "simple"}'))

    assert len(jobs) == 1
    job = jobs[0]
    assert job.id != None
    job = client.call(JobStatus(id=job.id, wait=True))
    assert job.status == "SUCCESS"
    assert job.ready == True
    assert type(job.result["url"]) == str

def test_job_wait_on_failure(indico):
    client = IndicoClient()
    dataset_filepath = str(Path(__file__).parents[1]) + "/data/mock.pdf"
    
    jobs = client.call(DocumentExtraction(files=[dataset_filepath], json_config='{"preset_config": "wrong"}'))

    assert len(jobs) == 1
    job = jobs[0]
    assert job.id != None
    job = client.call(JobStatus(id=job.id, wait=True))
    assert job.status == "FAILURE"
    assert type(job.result) == dict

def test_job_timeout(indico):
    client = IndicoClient()
    dataset_filepath = str(Path(__file__).parents[1]) + "/data/mock.pdf"
    job = client.call(DocumentExtraction(files=[dataset_filepath], json_config='{"preset_config": "detailed"}'))[0]
    with pytest.raises(IndicoTimeoutError):
        job = client.call(JobStatus(id=job.id, wait=True, timeout=0.))
