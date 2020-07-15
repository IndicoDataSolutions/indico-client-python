from indico import IndicoClient, IndicoConfig
from indico.filters import SubmissionFilter, or_
from indico.queries import (
    GenerateSubmissionResult,
    JobStatus,
    ListSubmissions,
    RetrieveStorageObject,
    SubmissionResult,
    WorkflowSubmission,
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
"""

submission_ids = client.call(
    WorkflowSubmission(workflow_id=workflow_id, files=["./path_to_doc.pdf"])
)
submission_id = submission_ids[0]

result_url = client.call(SubmissionResult(submission_id, wait=True))
result = client.call(RetrieveStorageObject(result_url.result))
print(result)


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
