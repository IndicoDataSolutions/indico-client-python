import json

from indico import IndicoClient
from indico.config.config import IndicoConfig
from indico.queries import WorkflowSubmissionFull, RetrieveStorageObject

workflow_id = 2979

client = IndicoClient(
    config=IndicoConfig(
        host="app.indico.io",
        api_token_path="/home/user/my_api_token.txt",
    )
)


def send_submission():
    files = ["/home/user/img1.jpg", "/home/user/img2.jpg"]
    # we create dictionary that will map:
    #   img1.jpg: sub_id
    #   img2.jpg: sub_id
    files_to_submission_ids = {f.split("/")[-1]: None for f in files}
    submissions = client.call(
        WorkflowSubmissionFull(workflow_id=workflow_id, files=files)
    )
    for sub in submissions:
        print(f"Submission id {sub.id} for file {sub.input_filename}")
        files_to_submission_ids[sub.input_filename] = sub.id

    return files_to_submission_ids


if __name__ == "__main__":
    submission_id = send_submission()
    # sqs_result = wait for sqs notification...
    # Example SQS Results:
    sqs_notif = {
        "submission_id": 3,
        "status": "SUCCESS",
        "result_url": "indico-file://...",  # a storage object
    }
    failed_sqs_notif = {
        "submission_id": 4,
        "status": "FAILURE",
        "result_url": "indico-file://...",
    }

    # Read in the result file for the completed submission
    result = client.call(RetrieveStorageObject(sqs_notif.result_url))
    print(
        f"Result for {sqs_notif['submission_id']} is:\n",
        json.dumps(result, indent=4)
    )
