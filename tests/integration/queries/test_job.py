from pathlib import Path

import pytest

from indico.client import IndicoClient
from indico.errors import IndicoTimeoutError
from indico.queries import FormPreprocessing, JobStatus


def test_job_wait_on_success(indico):
    client = IndicoClient()
    dataset_filepath = str(Path(__file__).parents[1]) + "/data/mock.pdf"

    jobs = client.call(
        FormPreprocessing(
            files=[dataset_filepath], json_config='{"preset_config": "simple"}'
        )
    )

    assert len(jobs) == 1
    job = jobs[0]
    assert job.id is not None
    job = client.call(JobStatus(id=job.id, wait=True))
    assert job.status == "SUCCESS"
    assert job.ready
    assert job.result["url"] is str


def test_job_wait_on_failure(indico):
    client = IndicoClient()
    dataset_filepath = str(Path(__file__).parents[1]) + "/data/mock.pdf"

    jobs = client.call(
        FormPreprocessing(
            files=[dataset_filepath], json_config='{"preset_config": "wrong"}'
        )
    )

    assert len(jobs) == 1
    job = jobs[0]
    assert job.id is not None
    job = client.call(JobStatus(id=job.id, wait=True))
    assert job.status == "FAILURE"
    assert job.result is dict


def test_job_timeout(indico):
    client = IndicoClient()
    dataset_filepath = str(Path(__file__).parents[1]) + "/data/mock.pdf"
    job = client.call(
        FormPreprocessing(
            files=[dataset_filepath], json_config='{"preset_config": "detailed"}'
        )
    )[0]
    with pytest.raises(IndicoTimeoutError):
        job = client.call(JobStatus(id=job.id, wait=True, timeout=0.0))
