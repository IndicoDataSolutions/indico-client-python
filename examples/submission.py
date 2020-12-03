from indico import IndicoClient, IndicoConfig
from indico.filters import SubmissionFilter, or_
from indico.queries import (
    GenerateSubmissionResult,
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
submission_id = submission_ids[0]

result_url = client.call(SubmissionResult(submission_id, wait=True))
result = client.call(RetrieveStorageObject(result_url.result))
print(result)

client.call(UpdateSubmission(submission_id, retrieved=True))

"""
Example 2
List all submissions that are COMPLETE or FAILED
Generate submission results for these
Delay gathering the results until required
"""
sub_filter = or_(SubmissionFilter(status="COMPLETE"), SubmissionFilter(status="FAILED"))
submissions = client.call(ListSubmissions(filters=sub_filter))

result_files = {
    submission: client.call(GenerateSubmissionResult(submission))
    for submission in submissions
}

# Do other fun things...

for submission, result_file_job in result_files.items():
    result_url = client.call(JobStatus(id=result_file_job.id, wait=True))
    result = client.call(RetrieveStorageObject(result_url.result))
    print(f"Submission {submission.id} has result:\n{result}")


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
    WorkflowSubmission(
        workflow_id=workflow_id, files=["my_file.pdf"]
    )
)
submissions = client.call(WaitForSubmissions(submission_ids))
submission = submissions[0]
raw_result = client.call(RetrieveStorageObject(submission.result_file))
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
