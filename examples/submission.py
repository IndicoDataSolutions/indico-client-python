from indico import IndicoClient, IndicoConfig
from indico.filters import SubmissionFilter, or_
from indico.queries import (
    JobStatus,
    ListSubmissions,
    RetrieveStorageObject,
    SubmissionResult,
    SubmitReview,
    UpdateSubmission,
    WaitForSubmissions,
    WorkflowSubmission,
    WorkflowSubmissionDetailed,
)

# Create an Indico API client
my_config = IndicoConfig(
    host="app.indico.io", api_token_path="./path/to/indico_api_token.txt"
)
client = IndicoClient(config=my_config)

workflow_id = 5

"""
Example 1
Create a new submission
Generate a submission result as soon as the submission is done processing
Then mark the submission has having been retrieved
"""

submission_ids = client.call(
    WorkflowSubmission(workflow_id=workflow_id, files=["./path_to_doc.pdf"])
)

job = client.call(SubmissionResult(submission_ids[0], wait=True))
result = client.call(RetrieveStorageObject(job.result))
print(result)
client.call(UpdateSubmission(submission_ids[0], retrieved=True))

"""
Example 2
List all submissions that are COMPLETE or FAILED
Retrieve submission results for all COMPLETE and check errors on any FAILED
"""
sub_filter = or_(SubmissionFilter(status="COMPLETE"), SubmissionFilter(status="FAILED"))
submissions = client.call(ListSubmissions(filters=sub_filter))

for submission in submissions:
    if submission.status == "COMPLETE":
        result = client.call(RetrieveStorageObject(submission.result_file))
        print(f"Submission {submission.id} has result:\n{result}")
    else:
        print(f"Submission {submission.id} failed:\n{submission.errors}")


"""
Example 3
Submit urls to a workflow
"""
submissions = client.call(
    WorkflowSubmissionDetailed(
        workflow_id=workflow_id, urls=["https://my_url.com/img.png"]
    )
)
submission = submission[0]

result_url = client.call(SubmissionResult(submission.id, wait=True))
result = client.call(RetrieveStorageObject(result_url.result))
print(result)

client.call(UpdateSubmission(submission.id, retrieved=True))


"""
Example 4
Submit "auto-review" for a submission
Requires auto-review is enabled for workflow
"""
submission_ids = client.call(
    WorkflowSubmission(workflow_id=workflow_id, files=["my_file.pdf"])
)
submissions = client.call(WaitForSubmissions(submission_ids))
submission = submissions[0]
raw_result = client.call(RetrieveStorageObject(submission.result_file))
changes = raw_result["results"]["document"]["results"]
rejected = False
for model, preds in changes.items():
    if isinstance(preds, dict):
        preds["accepted"] = True
    elif isinstance(preds, list):
        for pred in preds:
            pred["accepted"] = True
    else:
        rejected = True
print(f"Submitting review for {submission.id}: {changes}")
job = client.call(SubmitReview(submission.id, changes=changes, rejected=rejected))
job = client.call(JobStatus(job.id))
print("Review", job.id, "has result", job.result)

"""
Example 5
Use the client paginator to retrieve all PROCESSING submissions
Without the paginator, the hard limit is 1000
"""
sub_filter = SubmissionFilter(status="PROCESSING")
for submission in client.paginate(ListSubmissions(filters=sub_filter)):
    print(f"Submission {submission.id}")
    # do other cool things
