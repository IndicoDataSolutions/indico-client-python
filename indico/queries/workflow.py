import io
import tempfile
from typing import TYPE_CHECKING

from indico.client.request import Delay, GraphQLRequest, RequestChain
from indico.errors import IndicoError, IndicoInputError
from indico.queries.storage import UploadBatched, UploadDocument
from indico.types import SUBMISSION_RESULT_VERSIONS, Submission, Workflow
from indico.types.utils import cc_to_snake, snake_to_cc

if TYPE_CHECKING:  # pragma: no cover
    from typing import Any, ClassVar, Dict, Iterator, List, Optional, Union

    from indico.typing import Payload


class ListWorkflows(GraphQLRequest["List[Workflow]"]):
    """
    List all workflows visible to authenticated user

    Options:
        dataset_ids (List[int]): List of dataset ids to filter by
        workflow_ids (List[int]): List of workflow ids to filter by

    Returns:
        List[Workflow]: All the found Workflow objects
    """

    query = """
        query ListWorkflows($datasetIds: [Int], $workflowIds: [Int], $limit: Int){
            workflows(datasetIds: $datasetIds, workflowIds: $workflowIds, limit: $limit){
                workflows {
                    id
                    name
                    status
                    reviewEnabled
                    autoReviewEnabled
                    createdAt
                    createdBy
                    submissionRunnable
                components {
                        id
                        componentType
                        reviewable
                        filteredClasses
                        ... on ContentLengthComponent
                        {
                                minimum
                                maximum
                                }
                        ... on ModelGroupComponent {
                            taskType
                            modelType
                            modelGroup {
                                        status
                                      id
                                      name
                                      taskType
                                      questionnaireId
                                      classNames
                                      selectedModel{
                                        id
                                      }
                                }

                        }

                    }
                  componentLinks {
                    id
                    headComponentId
                    tailComponentId
                    config
                    filters {
                      classes
                    }

                  }
                  datasetId
                }
            }
        }
    """

    def __init__(
        self,
        *,
        dataset_ids: "Optional[List[int]]" = None,
        workflow_ids: "Optional[List[int]]" = None,
        limit: int = 100,
    ):
        super().__init__(
            self.query,
            variables={
                "datasetIds": dataset_ids,
                "workflowIds": workflow_ids,
                "limit": limit,
            },
        )

    def process_response(self, response: "Payload") -> "List[Workflow]":
        return [
            Workflow(**w)
            for w in super().parse_payload(response)["workflows"]["workflows"]
        ]


class GetWorkflow(GraphQLRequest["Workflow"]):
    """
    Query for Workflow by id

    Args:
        workflow_id (int): Workflow id to query for

    Returns:
        Workflow: Found Workflow object
    """

    def __init__(self, workflow_id: int):
        super().__init__(
            ListWorkflows.query,
            variables={"datasetIds": None, "workflowIds": [workflow_id], "limit": 100},
        )

    def process_response(self, response: "Payload") -> "Workflow":
        return Workflow(**super().parse_payload(response)["workflows"]["workflows"][0])


class _ToggleReview(GraphQLRequest["Workflow"]):
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

    def process_response(self, response: "Payload") -> "Workflow":
        return Workflow(**super().parse_payload(response)[self.query_name])


class _ToggleAutoReview(_ToggleReview):
    toggle = "enableAutoReview"
    query_name = "toggleWorkflowAutoReview"


class UpdateWorkflowSettings(RequestChain["Workflow"]):
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
        workflow: "Union[Workflow, int]",
        enable_review: "Optional[bool]" = None,
        enable_auto_review: "Optional[bool]" = None,
    ):
        self.workflow_id = workflow.id if isinstance(workflow, Workflow) else workflow
        if enable_review is None and enable_auto_review is None:
            raise IndicoInputError("Must provide at least one review option")

        self.enable_review = enable_review
        self.enable_auto_review = enable_auto_review

    def requests(self) -> "Iterator[_ToggleReview]":
        if self.enable_review is not None:
            yield _ToggleReview(self.workflow_id, self.enable_review)
        if self.enable_auto_review is not None:
            yield _ToggleAutoReview(self.workflow_id, self.enable_auto_review)


class _WorkflowSubmission(GraphQLRequest["Union[List[Submission], List[int]]"]):
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
        "bundle": "Boolean",
        "resultVersion": "SubmissionResultVersion",
    }

    def __init__(
        self,
        detailed_response: bool,
        **kwargs: "Any",
    ):
        self.workflow_id = kwargs["workflow_id"]

        # construct mutation signature and args based on provided kwargs to ensure
        # backwards-compatible graphql calls
        #
        # inputFiles, bundle, and resultVersion only available on IPA 4.9.0+
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

        args_list: "List[str]" = [
            _arg for _arg in self.mutation_args.keys() if kwargs.get(cc_to_snake(_arg))
        ]
        signature: str = ",".join(
            f"${_arg}: {self.mutation_args[_arg]}" for _arg in args_list
        )
        args: str = ",".join(f"{_arg}: ${_arg}" for _arg in args_list)

        super().__init__(
            query=q.format(
                mutation_name=self.mutation_name, signature=signature, args=args
            ),
            variables={snake_to_cc(var): val for var, val in kwargs.items()},
        )

    def process_response(
        self, response: "Payload"
    ) -> "Union[List[Submission], List[int]]":
        response = super().parse_payload(response)[self.mutation_name]
        if "submissions" in response:
            return [Submission(**s) for s in response["submissions"]]
        if not response["submissionIds"]:
            raise IndicoError(f"Failed to submit to workflow {self.workflow_id}")
        else:
            sub_ids: "List[int]" = response["submissionIds"]
            return sub_ids


class _WorkflowUrlSubmission(_WorkflowSubmission):
    mutation_name = "workflowUrlSubmission"
    mutation_args = {**_WorkflowSubmission.mutation_args, "urls": "[String]!"}
    del mutation_args["files"]


class WorkflowSubmission(RequestChain["Union[List[Submission], List[int]]"]):
    f"""
    Submit files to a workflow for processing.
    One of `files`, `urls`, `stream`, or `text` is required.

    Args:
        workflow_id (int): Id of workflow to submit files to
        files (List[str], optional): List of local file paths to submit
        urls (List[str], optional): List of urls to submit
        submission (bool, optional): DEPRECATED - AsyncJobs are no longer supported.
        bundle (bool, optional): Batch all files under a single submission id
        result_version (str, optional):
            The format of the submission result file. One of:
                {SUBMISSION_RESULT_VERSIONS}
            If bundle is enabled, this must be version TWO or later.
        streams (Dict[str, io.BufferedIOBase]): List of filename keys mapped to streams
            for upload. Similar to files but mutually exclusive with files.
            Can take for example: io.BufferedReader, io.BinaryIO, or io.BytesIO.
        text (str, optional): text to submit. Note: submission may still go through OCR.
        batch_size (int, optional): If submitting files, specifies the amount of files to submit in a single batch. Defaults to 10. A call with a batch exceeding 500mb total will fail with an error.

    Returns:
        List[int]: If `submission`, these will be submission ids.
            Otherwise, they will be AsyncJob ids.

    """

    detailed_response: "ClassVar[bool]" = False

    def __init__(
        self,
        workflow_id: int,
        files: "Optional[List[str]]" = None,
        urls: "Optional[List[str]]" = None,
        submission: bool = True,
        bundle: bool = False,
        result_version: "Optional[str]" = None,
        streams: "Optional[Dict[str, io.BufferedIOBase]]" = None,
        text: str = "",
        batch_size: int = 10,
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
        self.text = text
        self.batch_size = batch_size
        if not submission:
            raise IndicoInputError("This option is deprecated and no longer supported.")
        if not self.files and not self.urls and not self.has_streams and not self.text:
            raise IndicoInputError(
                "One of 'files', 'streams', 'urls', or 'text' must be specified"
            )
        elif (self.files or self.urls or self.text) and self.has_streams:
            raise IndicoInputError(
                "Only one of 'files' or 'streams', 'urls', or 'text' may be specified."
            )
        elif (self.files or self.text) and self.urls:
            raise IndicoInputError(
                "Only one of 'files' or 'streams', 'urls', or 'text' may be specified"
            )
        elif self.files and self.text:
            raise IndicoInputError(
                "Only one of 'files' or 'streams', 'urls', or 'text' may be specified"
            )

    def requests(
        self,
    ) -> "Iterator[Union[UploadBatched, UploadDocument, _WorkflowSubmission]]":
        if self.files:
            yield UploadBatched(files=self.files, batch_size=self.batch_size)
            yield _WorkflowSubmission(
                self.detailed_response,
                workflow_id=self.workflow_id,
                files=self.previous,
                bundle=self.bundle,
                result_version=self.result_version,
            )
        elif self.urls:
            yield _WorkflowUrlSubmission(
                self.detailed_response,
                workflow_id=self.workflow_id,
                urls=self.urls,
                bundle=self.bundle,
                result_version=self.result_version,
            )
        elif self.has_streams:
            yield UploadDocument(streams=self.streams)
            yield _WorkflowSubmission(
                self.detailed_response,
                workflow_id=self.workflow_id,
                files=self.previous,
                bundle=self.bundle,
                result_version=self.result_version,
            )
        elif self.text:
            temp = tempfile.NamedTemporaryFile(mode="w+", suffix=".txt")
            try:
                temp.write(self.text)
                temp.seek(0)
                yield UploadDocument(files=[temp.name])
                yield _WorkflowSubmission(
                    self.detailed_response,
                    workflow_id=self.workflow_id,
                    files=self.previous,
                    bundle=self.bundle,
                    result_version=self.result_version,
                )
            finally:
                temp.close()


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

    detailed_response: "ClassVar[bool]" = True

    def __init__(
        self,
        workflow_id: int,
        files: "Optional[List[str]]" = None,
        urls: "Optional[List[str]]" = None,
        bundle: bool = False,
        result_version: "Optional[str]" = None,
    ):
        super().__init__(
            workflow_id,
            files=files,
            urls=urls,
            submission=True,
            bundle=bundle,
            result_version=result_version,
        )


class _AddDataToWorkflow(GraphQLRequest["Workflow"]):
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

    def process_response(self, response: "Payload") -> "Workflow":
        return Workflow(
            **super().parse_payload(response)["addDataToWorkflow"]["workflow"]
        )


class AddDataToWorkflow(RequestChain["Workflow"]):
    """
    Mutation to update data in a workflow, presumably
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

    def requests(self) -> "Iterator[Union[_AddDataToWorkflow, Delay, GetWorkflow]]":
        yield _AddDataToWorkflow(self.workflow_id)

        if self.wait:
            while self.previous.status != "COMPLETE":
                yield Delay()
                yield GetWorkflow(workflow_id=self.workflow_id)


class CreateWorkflow(GraphQLRequest["Workflow"]):
    """
    Mutation to create workflow given an existing dataset.

    Args:
        dataset_id(int): dataset to create workflow for
        name(str): name for the workflow

    """

    query = """  mutation createWorkflow($datasetId: Int!, $name: String!) {
    createWorkflow(datasetId: $datasetId, name: $name) {
           workflow {
                    id
                    name
                    status
                    reviewEnabled
                    autoReviewEnabled
                    submissionRunnable
                components {
                        id
                        componentType
                        reviewable
                        filteredClasses

                        ... on ModelGroupComponent {
                            taskType
                            modelType
                        }

                    }
                  componentLinks{
                    id
                    headComponentId
                    tailComponentId
                    filters {
                      classes
                    }

                  }
                }
    }
    }
    """

    def __init__(self, dataset_id: int, name: str):
        super().__init__(
            self.query,
            variables={"datasetId": dataset_id, "name": name},
        )

    def process_response(self, response: "Payload") -> "Workflow":
        return Workflow(**super().parse_payload(response)["createWorkflow"]["workflow"])


class DeleteWorkflow(GraphQLRequest[bool]):
    """
    Mutation to delete workflow given workflow id. Note that this operation includes deleting
    all components and models associated with this workflow.

    Args:
        workflow_id(int): id of workflow to delete
    """

    query = """
        mutation deleteWorkflow($workflowId: Int!){
            deleteWorkflow(workflowId: $workflowId){
                success
            }
        }
    """

    def __init__(self, workflow_id: int):
        super().__init__(self.query, variables={"workflowId": workflow_id})

    def process_response(self, response: "Payload") -> bool:
        status: bool = super().parse_payload(response)["deleteWorkflow"]["success"]
        return status
