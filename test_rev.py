
import json
import os
import time

from indico import IndicoClient
from indico.config.config import IndicoConfig
from indico.queries import *  # noqa

workflow_id = 1632   # dev invoices
invoices_dir = "/home/astha/Downloads/samples/invoices"
invoices = [invoices_dir + f"/{i}" for i in os.listdir(invoices_dir)]

devconf = IndicoConfig(
    host="dev.indico.io",
    api_token_path="/home/astha/Downloads/indico_api_token_dev.txt",
)

client = IndicoClient(config=devconf)

def main(noval=None):
    _mfiles = invoices[2:3]
    print(f"Invoices: {_mfiles}")
    submission_ids = client.call(WorkflowSubmission(workflow_id=workflow_id, files=_mfiles))
    print("Made submissions", submission_ids)
    # Submissions are made! Wait for them to get to PENDING_AUTO_REVIEW
    submissions = client.call(WaitForSubmissions(submission_ids, timeout=120))
    print("Waited submissions", [(s.id, s.status, s.result_file) for s in submissions])
    # First submission - accept and reject a couple things
    submission = submissions[0]
    raw_result = client.call(RetrieveStorageObject(submission.result_file))
    changes = raw_result["results"]["document"]["results"]
    print(f"orig changes\n", changes)
    rejected = False
    update = None
    for model, preds in changes.items():
        if isinstance(preds, dict):
            # class model result
            preds["accepted"] = True
        elif isinstance(preds, list):
            if noval:
                update = {model: "NO VALUE"}
            else:
                # extraction model
                preds[0]["accepted"] = True
                preds[1]["rejected"] = True
                preds[2]["accepted"] = True
        else:
            pass
            # rejected = True
    if update:
        changes.update(update)
    print("Changes", changes)
    job = client.call(SubmitReview(submission.id, changes=changes, rejected=rejected))
    job = client.call(JobStatus(job.id))
    print(job.id, "has result", job.result)
    submission = client.call(GetSubmission(submission.id))
    print(f"Sub now has {submission.status}")



if __name__ == "__main__":
    # main()
    main(noval=True)
