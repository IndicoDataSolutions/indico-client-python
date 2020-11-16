from typing import List

from indico.client.request import GraphQLRequest, RequestChain
from indico.errors import IndicoError, IndicoInputError
from indico.queries.storage import UploadDocument
from indico.types import Job, Submission, Workflow


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
                    reviewEnabled
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


class _WorkflowSubmission(GraphQLRequest):

    query = """
        mutation workflowSubmissionMutation($workflowId: Int!, ${arg_}: {type_}, $recordSubmission: Boolean) {{
            {mutation_name}(workflowId: $workflowId, {arg_}: ${arg_}, recordSubmission: $recordSubmission) {{
                jobIds
                submissionIds
            }}
        }}
    """

    detailed_query = """
        mutation workflowSubmissionMutation($workflowId: Int!, ${arg_}: {type_}, $recordSubmission: Boolean) {{
            {mutation_name}(workflowId: $workflowId, {arg_}: ${arg_}, recordSubmission: $recordSubmission) {{
                submissionIds
                submissions {{
                    id
                    datasetId
                    workflowId
                    status
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
    """
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
    ):
        self.workflow_id = workflow_id
        self.files = files
        self.urls = urls
        self.submission = submission
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
            )
        elif self.urls:
            yield _WorkflowUrlSubmission(
                workflow_id=self.workflow_id,
                urls=self.urls,
                submission=self.submission,
                detailed_response=self.detailed_response,
            )


class WorkflowSubmissionDetailed(WorkflowSubmission):
    """
    Submit files to a workflow for processing.
    One of `files` or `urls` is required.
    Submission recording is mandatory.

    Args:
        workflow_id (int): Id of workflow to submit files to
        files (List[str], optional): List of local file paths to submit
        urls (List[str], optional): List of urls to submit

    Returns:
        List[Submission]: Submission objects created

    """

    detailed_response = True

    def __init__(
        self, workflow_id: int, files: List[str] = None, urls: List[str] = None
    ):
        super().__init__(workflow_id, files=files, urls=urls, submission=True)
