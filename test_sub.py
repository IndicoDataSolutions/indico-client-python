import json
import os
import time

from indico import IndicoClient
from indico.config.config import IndicoConfig
from indico.queries import JobStatus, WorkflowSubmission, ModelGroupPredict, WorkflowSubmissionDetailed
from indico.queries.storage import (
    URL_PREFIX,
    RetrieveStorageObject,
    UploadDocument,
)
from indico.queries.submission import SubmissionResult, GetSubmission
from indico.queries.workflow import ListWorkflows

# workflow_id = 1632   # dev invoices
# workflow_id = 2979  # dev obj detection
workflow_id = 1  # leak invoices
invoices_dir = "/home/astha/Downloads/samples/invoices"
invoices = [invoices_dir + f"/{i}" for i in os.listdir(invoices_dir)]
image_file = "/home/astha/Pictures/cat.png"
image_files = [
    f"/home/astha/indico/indico-client-python/tests/integration/data/{i}.jpg"
    for i in range(1, 26)
]
# image_urls = "/home/astha/indico/indico-client-python/customout_list.json"
image_urls = "/home/astha/indico/indico-client-python/devout_list.json"
wm_images_dir = "/home/astha/Downloads/wm_obj_detection_images"
wm_images = [wm_images_dir + f"/{i}" for i in os.listdir(wm_images_dir)]
external_wm_url = "https://astha-test-data.s3.us-east-1.amazonaws.com/test_img.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIAI4OPWIAU64DRVFRQ%2F20201013%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Date=20201013T234323Z&X-Amz-Expires=604800&X-Amz-SignedHeaders=host&X-Amz-Signature=9f3a003d8ce83c3f8539a6539cdff3aadd71537dc1f619f35df84be80920287b"

devconf = IndicoConfig(
    host="dev.indico.io",
    api_token_path="/home/astha/Downloads/indico_api_token_dev.txt",
)

rrconf = IndicoConfig(
    host="dev.indico.io",
    api_token_path="/home/astha/Downloads/indico_api_token_rr.txt",
)


featconf = IndicoConfig(
    host="dev-sunleak.indico.io",
    api_token_path="/home/astha/Downloads/indico_api_token_sunleak.txt",
)

client = IndicoClient(config=featconf)


def create_multi_subs():
    _mfiles = invoices[:5]
    print(f"Invoices: {_mfiles}")
    subs = client.call(WorkflowSubmission(workflow_id=workflow_id, files=_mfiles))
    print("Made subs:", subs)


def create_results(submission_id=2):
    result_url = client.call(SubmissionResult(submission_id, wait=True))
    result_url = result_url.result
    print("result url:", result_url)
    result = client.call(RetrieveStorageObject(result_url))
    print(json.dumps(result, indent=4))


def list_workflows():
    workflows = client.call(ListWorkflows())
    print(workflows)


def image_flow(w_id=2979):
    start = time.time()
    loops = 100
    b_size = 100
    last_sub = None
    for i in range(loops):  # 500
        print(f"Sending Batch {i}")
        subs = client.call(
            WorkflowSubmission(workflow_id=w_id, urls=[external_wm_url]*b_size)
            # WorkflowSubmission(workflow_id=w_id, files=wm_images[:1])
        )
        # for sub in subs:
        #     print(f"Submission id {sub.id} for file {sub.input_filename}")
        # job = subs[0]
        # status = client.call(JobStatus(id=job.id, wait=True))
        # wf_result = client.call(RetrieveStorageObject(status.result))
        # print(wf_result)
        last_sub = subs[-1]
        time.sleep(5)
        # result = client.call(RetrieveStorageObject(result_url.result))
        # print(json.dumps(result, indent=4))
    print(f"Waiting for final sub...")
    client.call(SubmissionResult(last_sub, wait=True, timeout=1000))
    print(f"Batch of {loops * b_size} took {time.time() - start}")


def objdetect_test():
    MODEL_ID = 4641
    storage_urls = []
    with open(image_urls, "r") as f:
        storage_urls = json.load(f)
    storage_urls = storage_urls[:3]  # * 48  # 25 * 48 = 1200 objects
    # batch_sizes = (300, 100, 50, 30, 1)
    batch_sizes = (50,)
    print(f"Testing with {len(storage_urls)}")
    for batch_size in batch_sizes:
        start = time.time()
        for i in range(0, len(storage_urls), batch_size):
            job = client.call(
                ModelGroupPredict(
                    model_id=MODEL_ID,
                    data=storage_urls[i : i + batch_size],
                    predict_options={"threshold": 0.25},
                    load=False,
                )
            )
            result = client.call(JobStatus(job.id, wait=True))
            print(f"Result for {job.id} is {result.result}")
        # print(f"Batch size {batch_size} processed in {time.time() - start}")


def make_urls():
    response = client.call(UploadDocument(files=wm_images))
    storage_urls = [URL_PREFIX + json.loads(r["filemeta"])["path"] for r in response]
    with open(image_urls, "w") as f:
        json.dump(storage_urls, f, indent=4)
    return storage_urls


if __name__ == "__main__":
    create_multi_subs()
    # create_results(sub_id)
    # image_flow(workflow_id)
    # make_urls()
    # objdetect_test()
    # create_multi_subs()
