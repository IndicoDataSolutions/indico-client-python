from pathlib import Path
from indico.client import IndicoClient
from indico.queries import RetrieveStorageObject, JobStatus, WorkflowSubmission
from indico.types.jobs import Job

def test_workflow_submission(indico):
    client = IndicoClient()
    dataset_filepath = str(Path(__file__).parents[1]) + "/data/mock.pdf"
    
    jobs = client.call(WorkflowSubmission(workflow_id=0, files=[dataset_filepath]))

    assert len(jobs) == 1
    job = jobs[0]
    assert job.id != None
    job = client.call(JobStatus(id=job.id, wait=True))
    assert job.status == "SUCCESS"
    assert job.ready == True
    assert type(job.result["url"]) == str

    extract = client.call(RetrieveStorageObject(
        job.result
    ))

    assert type(extract) == dict
    assert "pages" in extract

