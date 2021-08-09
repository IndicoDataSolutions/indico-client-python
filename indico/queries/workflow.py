import io
from typing import List, Union, Dict

from indico.client.request import GraphQLRequest, RequestChain, Debouncer
from indico.errors import IndicoError, IndicoInputError
from indico.queries.storage import UploadDocument
from indico.types import Job, Submission, Workflow, SUBMISSION_RESULT_VERSIONS
from indico.types.utils import cc_to_snake, snake_to_cc


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
            query,
            variables={"workflowId": workflow_id, "reviewState": enable_review},
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
        mutation workflowSubmissionMutation({signature}) {{
            {mutation_name}({args}) {{
                jobIds
                submissionIds
            }}
        }}
    """

    detailed_query = """
        mutation workflowSubmissionMutation({signature}) {{
            {mutation_name}({args}) {{
                submissionIds
                submissions {{
                    id
                    datasetId
                    workflowId
                    status
                    <SUBQUERY>
                    inputFile
                    inputFilename
                    resultFile
                    retrieved
                    errors
                }}
            }}
        }}
    """
    files_subquery = """
        inputFiles {{
            filepath
            filename
        }}
    """.strip()

    mutation_name = "workflowSubmission"
    mutation_args = {
        "workflowId": "Int!",
        "files": "[FileInput]!",
        "recordSubmission": "Boolean",
        "bundle": "Boolean",
        "resultVersion": "SubmissionResultVersion",
    }

    def __init__(
            self,
            detailed_response: bool,
            **kwargs,
    ):
        self.workflow_id = kwargs["workflow_id"]
        self.record_submission = kwargs["record_submission"]

        # construct mutation signature and args based on provided kwargs to ensure
        # backwards-compatible graphql calls
        #
        # inputFiles, bundle, and resultVersion only avaliable on IPA 4.9.0+
        subq = (
            self.files_subquery
            if kwargs.get("bundle") or kwargs.get("result_version")
            else ""
        )
        q = (
            self.detailed_query.replace("<SUBQUERY>", subq)
            if detailed_response
            else self.query
        )

        args = [
            _arg for _arg in self.mutation_args.keys() if kwargs.get(cc_to_snake(_arg))
        ]
        signature = ",".join(f"${_arg}: {self.mutation_args[_arg]}" for _arg in args)
        args = ",".join(f"{_arg}: ${_arg}" for _arg in args)

        super().__init__(
            query=q.format(
                mutation_name=self.mutation_name, signature=signature, args=args
            ),
            variables={snake_to_cc(var): val for var, val in kwargs.items()},
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
    mutation_name = "workflowUrlSubmission"
    mutation_args = {**_WorkflowSubmission.mutation_args, "urls": "[String]!"}
    del mutation_args["files"]


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
        streams (Dict[str, io.BufferedIOBase]): List of filename keys mapped to streams
            for upload. Similar to files but mutually exclusive with files. 
            Can take for example: io.BufferedReader, io.BinaryIO, or io.BytesIO.

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
            streams: Dict[str, io.BufferedIOBase] = None
    ):
        self.workflow_id = workflow_id
        self.files = files
        self.urls = urls
        self.submission = submission
        self.bundle = bundle
        self.result_version = result_version
        self.has_streams = False
        if streams is not None:
            self.streams = streams.copy()
            self.has_streams = True
        else:
            self.streams = None

        if not self.files and not self.urls and not self.has_streams:
            raise IndicoInputError("One of 'files', 'streams', or 'urls' must be specified")
        elif self.files and self.has_streams:
            raise IndicoInputError("Only one of 'files' or 'streams' or 'urls' may be specified.")
        elif (self.files or self.has_streams) and self.urls:
            raise IndicoInputError("Only one of 'files' or 'streams' or 'urls' may be specified")

    def requests(self):
        if self.files:
            yield UploadDocument(files=self.files)
            yield _WorkflowSubmission(
                self.detailed_response,
                workflow_id=self.workflow_id,
                record_submission=self.submission,
                files=self.previous,
                bundle=self.bundle,
                result_version=self.result_version,
            )
        elif self.urls:
            yield _WorkflowUrlSubmission(
                self.detailed_response,
                workflow_id=self.workflow_id,
                record_submission=self.submission,
                urls=self.urls,
                bundle=self.bundle,
                result_version=self.result_version,
            )
        elif self.has_streams:
            yield UploadDocument(streams=self.streams)
            yield _WorkflowSubmission(
                self.detailed_response,
                workflow_id=self.workflow_id,
                record_submission=self.submission,
                files=self.previous,
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
            self.query,
            variables={"workflowId": workflow_id},
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
