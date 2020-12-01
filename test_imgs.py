from indico import IndicoClient
from indico.config.config import IndicoConfig
from indico.queries import JobStatus, RetrieveStorageObject, WorkflowSubmission

image_file = "/home/astha/Pictures/cat.png"
client = IndicoClient(
    config=IndicoConfig(
        host="dev-customout.indico.io",
        api_token_path="/home/astha/Downloads/indico_api_token_custom.txt",
    )
)


def image_flow(w_id):
    # 11 - kitten or bear classification
    # 12 - cats and dogs obj detection
    jobs = client.call(
        WorkflowSubmission(workflow_id=w_id, files=[image_file], submission=False)
        # WorkflowSubmission(workflow_id=w_id, files=image_files[:1], submission=False)
    )
    job = jobs[0]
    status = client.call(JobStatus(id=job.id, wait=True))
    wf_result = client.call(RetrieveStorageObject(status.result))
    print(wf_result)


if __name__ == "__main__":
    image_flow(11)
