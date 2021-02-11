from typing import List, Union

from indico.client.request import GraphQLRequest, RequestChain, Debouncer
from indico.errors import IndicoError, IndicoInputError
from indico.queries.storage import UploadDocument
from indico.types import Job, Submission, Workflow, SUBMISSION_RESULT_VERSIONS


class ListWorkflows(GraphQLRequest):
    """
    List all workflows visible to authenticated user

    Options:
        dataset_ids (List[int]): List of dataset ids to filter by
        workflow_ids (List[int]): List of workflow ids to filter by

    Returns:
        List[Workflow]: All the found Workflow objects
    """

    query = """
        query ListWorkflows($datasetIds: [Int], $workflowIds: [Int]){
            workflows(datasetIds: $datasetIds, workflowIds: $workflowIds){
                workflows {
                    id
                    name
                    status
                    reviewEnabled
                    autoReviewEnabled
                }
            }
        }
    """

    def __init__(
        self, *, dataset_ids: List[int] = None, workflow_ids: List[int] = None
    ):
        super().__init__(
            self.query,
            variables={"datasetIds": dataset_ids, "workflowIds": workflow_ids},
        )

    def process_response(self, response) -> List[Workflow]:
        return [
            Workflow(**w)
            for w in super().process_response(response)["workflows"]["workflows"]
        ]


class GetWorkflow(ListWorkflows):
    """
    Query for Workflow by id

    Args:
        workflow_id (int): Workflow id to query for

    Returns:
        Workflow: Found Workflow object
    """

    def __init__(self, workflow_id: int):
        super().__init__(workflow_ids=[workflow_id])

    def process_response(self, response) -> Workflow:
        return super().process_response(response)[0]


class _ToggleReview(GraphQLRequest):
    toggle = "enableReview"
    query_name = "toggleWorkflowReview"
    query = """
        mutation ToggleReview($workflowId: Int!, $reviewState: Boolean!){
            <QUERY NAME>(workflowId: $workflowId, <TOGGLE>: $reviewState){
                id
                name
                reviewEnabled
                autoReviewEnabled
            }
        }
    """

    def __init__(self, workflow_id: int, enable_review: bool):
        query = self.query.replace("<QUERY NAME>", self.query_name)
        query = query.replace("<TOGGLE>", self.toggle)
        super().__init__(
            query, variables={"workflowId": workflow_id, "reviewState": enable_review},
        )

    def process_response(self, response) -> Workflow:
        return Workflow(**super().process_response(response)[self.query_name])


class _ToggleAutoReview(_ToggleReview):
    toggle = "enableAutoReview"
    query_name = "toggleWorkflowAutoReview"


class UpdateWorkflowSettings(RequestChain):
    """
    Mutation to toggle review and auto-review on a workflow

    Args:
        workflow (int|Workflow): Workflow or workflow id to update

    Options:
        enable_review (bool): Enable review
        enable_auto_review (bool): Enable auto_review

    Returns:
        Workflow: Updated Workflow object
    """

    def __init__(
        self,
        workflow: Union[Workflow, int],
        enable_review: bool = None,
        enable_auto_review: bool = None,
    ):
        self.workflow_id = workflow.id if isinstance(workflow, Workflow) else workflow
        if enable_review is None and enable_auto_review is None:
            raise IndicoInputError("Must provide at least one review option")

        self.enable_review = enable_review
        self.enable_auto_review = enable_auto_review

    def requests(self):
        if self.enable_review is not None:
            yield _ToggleReview(self.workflow_id, self.enable_review)
        if self.enable_auto_review is not None:
            yield _ToggleAutoReview(self.workflow_id, self.enable_auto_review)


class _WorkflowSubmission(GraphQLRequest):

    query = """
        mutation workflowSubmissionMutation($workflowId: Int!, ${arg_}: {type_}, $recordSubmission: Boolean, $bundle: Boolean, $resultVersion: SubmissionResultVersion) {{
            {mutation_name}(workflowId: $workflowId, {arg_}: ${arg_}, recordSubmission: $recordSubmission, bundle: $bundle, resultVersion: $resultVersion) {{
                jobIds
                submissionIds
            }}
        }}
    """

    detailed_query = """
        mutation workflowSubmissionMutation($workflowId: Int!, ${arg_}: {type_}, $recordSubmission: Boolean, $bundle: Boolean, $resultVersion: SubmissionResultVersion) {{
            {mutation_name}(workflowId: $workflowId, {arg_}: ${arg_}, recordSubmission: $recordSubmission, bundle: $bundle, resultVersion: $resultVersion) {{
                submissionIds
                submissions {{
                    id
                    datasetId
                    workflowId
                    status
                    inputFiles {{
                        filepath
                        filename
                    }}
                    inputFile
                    inputFilename
                    resultFile
                    retrieved
                    errors
                }}
            }}
        }}
    """

    query_format = {"arg_": "files", "type_": "[FileInput]!"}
    mutation_name = "workflowSubmission"

    def __init__(
        self,
        workflow_id: int,
        submission: bool,
        files: List[str] = None,
        urls: List[str] = None,
        detailed_response: bool = False,
        bundle: bool = False,
        result_version: str = None,
    ):
        self.workflow_id = workflow_id
        self.record_submission = submission

        q = self.detailed_query if detailed_response else self.query

        super().__init__(
            query=q.format(mutation_name=self.mutation_name, **self.query_format),
            variables={
                "files": files,
                "urls": urls,
                "workflowId": workflow_id,
                "recordSubmission": submission,
                "bundle": bundle,
                "resultVersion": result_version,
            },
        )

    def process_response(self, response):
        response = super().process_response(response)[self.mutation_name]
        if "submissions" in response:
            return [Submission(**s) for s in response["submissions"]]
        elif self.record_submission:
            return response["submissionIds"]
        elif not response["jobIds"]:
            raise IndicoError(f"Failed to submit to workflow {self.workflow_id}")
        return [Job(id=job_id) for job_id in response["jobIds"]]


class _WorkflowUrlSubmission(_WorkflowSubmission):
    query_format = {"arg_": "urls", "type_": "[String]!"}
    mutation_name = "workflowUrlSubmission"


class WorkflowSubmission(RequestChain):
    f"""
    Submit files to a workflow for processing.
    One of `files` or `urls` is required.

    Args:
        workflow_id (int): Id of workflow to submit files to
        files (List[str], optional): List of local file paths to submit
        urls (List[str], optional): List of urls to submit
        submission (bool, optional): Process these files as normal submissions.
            Defaults to True.
            If False, files will be processed as AsyncJobs, ignoring any workflow
            post-processing steps like Review and with no record in the system
        bundle (bool, optional): Batch all files under a single submission id
        result_version (str, optional):
            The format of the submission result file. One of:
                {SUBMISSION_RESULT_VERSIONS}
            If bundle is enabled, this must be version TWO or later.

    Returns:
        List[int]: If `submission`, these will be submission ids.
            Otherwise, they will be AsyncJob ids.

    """

    detailed_response = False

    def __init__(
        self,
        workflow_id: int,
        files: List[str] = None,
        urls: List[str] = None,
        submission: bool = True,
        bundle: bool = False,
        result_version: str = None,
    ):
        self.workflow_id = workflow_id
        self.files = files
        self.urls = urls
        self.submission = submission
        self.bundle = bundle
        self.result_version = result_version

        if not self.files and not self.urls:
            raise IndicoInputError("One of 'files' or 'urls' must be specified")
        elif self.files and self.urls:
            raise IndicoInputError("Only one of 'files' or 'urls' must be specified")

    def requests(self):
        if self.files:
            yield UploadDocument(files=self.files)
            yield _WorkflowSubmission(
                workflow_id=self.workflow_id,
                files=self.previous,
                submission=self.submission,
                detailed_response=self.detailed_response,
                bundle=self.bundle,
                result_version=self.result_version,
            )
        elif self.urls:
            yield _WorkflowUrlSubmission(
                workflow_id=self.workflow_id,
                urls=self.urls,
                submission=self.submission,
                detailed_response=self.detailed_response,
                bundle=self.bundle,
                result_version=self.result_version,
            )


class WorkflowSubmissionDetailed(WorkflowSubmission):
    f"""
    Submit files to a workflow for processing.
    One of `files` or `urls` is required.
    Submission recording is mandatory.

    Args:
        workflow_id (int): Id of workflow to submit files to
        files (List[str], optional): List of local file paths to submit
        urls (List[str], optional): List of urls to submit
        bundle (bool, optional): Batch all files under a single submission id
        result_version (str, optional):
            The format of the submission result file. One of:
                {SUBMISSION_RESULT_VERSIONS}
            If bundle is enabled, this must be version TWO or later.

    Returns:
        List[Submission]: Submission objects created

    """

    detailed_response = True

    def __init__(
        self,
        workflow_id: int,
        files: List[str] = None,
        urls: List[str] = None,
        bundle: bool = False,
        result_version: str = None,
    ):
        super().__init__(
            workflow_id,
            files=files,
            urls=urls,
            submission=True,
            bundle=bundle,
            result_version=result_version,
        )


class _AddDataToWorkflow(GraphQLRequest):
    query = """
        mutation addDataToWorkflow($workflowId: Int!) {
            addDataToWorkflow(workflowId: $workflowId){
                workflow{
                    id
                    name
                    status
                }
            }
        }
    """

    def __init__(self, workflow_id: int):
        super().__init__(
            self.query, variables={"workflowId": workflow_id},
        )

    def process_response(self, response) -> Workflow:
        return Workflow(
            **super().process_response(response)["addDataToWorkflow"]["workflow"]
        )


class AddDataToWorkflow(RequestChain):
    """
    Mutation to update data in a workflow, pressumably
    after new data is added to the dataset.

    Args:
        workflow_id (int): Workflow id to update

    Options:
        wait (bool, default=False): Block while polling for status of update

    Returns:
        Workflow: Updated Workflow object
    """

    def __init__(self, workflow_id: int, wait: bool = False):
        self.workflow_id = workflow_id
        self.wait = wait

    def requests(self):
        yield _AddDataToWorkflow(self.workflow_id)

        if self.wait:
            debouncer = Debouncer()

            while self.previous.status != "COMPLETE":
                yield GetWorkflow(workflow_id=self.workflow_id)
                debouncer.backoff()
