from typing import TYPE_CHECKING

from indico.client.request import (
    GraphQLRequest,
    PagedRequestV2,
    RequestChain,
)
from indico.errors import IndicoInputError, IndicoRequestError
from indico.filters import FieldBlueprintFilter
from indico.queries.jobs import JobStatus
from indico.queries.storage import (
    ProxiedUpload,
    RetrieveStorageObject,
    parse_export_upload,
    storage_path,
)
from indico.types.field_blueprint import FieldBlueprint
from indico.types.jobs import Job
from indico.types.model_export import ExportUpload

if TYPE_CHECKING:  # pragma: no cover
    from typing import Any, Iterator, List, Optional, Union

    from indico.typing import AnyDict, Payload


class CreateFieldBlueprint(GraphQLRequest["List[FieldBlueprint]"]):
    """
    Create one or more field blueprints.

    Args:
        blueprints (List[dict]): List of field blueprint configurations to create.

    Returns:
        List[FieldBlueprint]: The newly created FieldBlueprint objects
    """

    query = """
    mutation CreateFieldBlueprint($blueprints: [CreateFieldBlueprintInput]!) {
        createFieldBlueprint(blueprints: $blueprints) {
            blueprints {
            id
            uid
            name
            version
            taskType
            tags
            enabled
            fieldConfig {
                ... on ExtractionFieldConfig {
                name
                datatype
                required
                multiple
                validationConfig
                formatConfig
                inputConfig
                }
            }
            promptConfig {
                ... on ExtractionPromptConfig {
                description
                targetName
                multipleValues
                minimumLocationType
                localization
                }
            }
            }
        }
    }
    """

    def __init__(self, blueprints: "List[AnyDict]"):
        super().__init__(
            self.query,
            variables={"blueprints": blueprints},
        )

    def process_response(self, response: "Payload") -> "List[FieldBlueprint]":
        data = super().parse_payload(response)["createFieldBlueprint"]["blueprints"]
        return [FieldBlueprint(**bp) for bp in data]


class GetFieldBlueprints(GraphQLRequest["List[FieldBlueprint]"]):
    """
    Get field blueprints by IDs.

    Args:
        ids (List[int]): List of field blueprint IDs to retrieve.

    Returns:
        List[FieldBlueprint]: List of retrieved FieldBlueprint objects
    """

    query: str = """
    query GetFieldBlueprints($ids: [Int]!) {
        gallery {
            fieldBlueprint {
                blueprints(ids: $ids) {
                    id
                    uid
                    name
                    version
                    taskType
                    tags
                    enabled
                    createdAt
                    updatedAt
                    createdBy
                    updatedBy
                    fieldConfig {
                        ... on ExtractionFieldConfig {
                            name
                            datatype
                            required
                            multiple
                            validationConfig
                            formatConfig
                            inputConfig
                        }
                    }
                    promptConfig {
                        ... on ExtractionPromptConfig {
                            description
                            localization
                            targetName
                            multipleValues
                            minimumLocationType
                        }
                    }
                }
            }
        }
    }
    """

    def __init__(self, ids: "List[int]"):
        super().__init__(self.query, variables={"ids": ids})

    def process_response(self, response: "Payload") -> "List[FieldBlueprint]":
        data = super().parse_payload(response)["gallery"]["fieldBlueprint"][
            "blueprints"
        ]
        return [FieldBlueprint(**bp) for bp in data]


class ListFieldBlueprints(PagedRequestV2["List[FieldBlueprint]"]):
    """
    List field blueprints with pagination.

    Args:
        limit (int, default=100): Max number of blueprints to retrieve per page
        cursor (str, optional): Cursor to fetch results from
        filters (Union[List[dict], FieldBlueprintFilter], optional): Filters to apply

    Returns:
        List[FieldBlueprint]
    """

    query = """
    query ListFieldBlueprints($size: Int, $cursor: String, $filters: FilterInput) {
        gallery {
            fieldBlueprint {
                blueprintsPage(size: $size, cursor: $cursor, filters: $filters) {
                    fieldBlueprints {
                        id
                        uid
                        name
                        version
                        taskType
                        tags
                        enabled
                        createdAt
                        updatedAt
                        createdBy
                        updatedBy
                        fieldConfig {
                            ... on ExtractionFieldConfig {
                                name
                                datatype
                                required
                                multiple
                                validationConfig
                                formatConfig
                                inputConfig
                            }
                        }
                        promptConfig {
                            ... on ExtractionPromptConfig {
                                description
                                localization
                                targetName
                                multipleValues
                                minimumLocationType
                            }
                        }
                    }
                    cursor
                    total
                }
            }
        }
    }
    """

    def __init__(
        self,
        limit: int = 100,
        cursor: "Optional[str]" = None,
        filters: "Union[Optional[AnyDict], FieldBlueprintFilter]" = None,
    ):
        super().__init__(
            self.query, variables={"size": limit, "cursor": cursor, "filters": filters}
        )

    def process_response(self, response: "Payload") -> "List[FieldBlueprint]":
        response_data = super().parse_payload(
            response, nested_keys=["gallery", "fieldBlueprint", "blueprintsPage"]
        )
        page = response_data["gallery"]["fieldBlueprint"]["blueprintsPage"]
        return [FieldBlueprint(**bp) for bp in page["fieldBlueprints"]]


class _ExportFieldBlueprints(GraphQLRequest["Job"]):
    query = """
    mutation ExportFieldBlueprints($fieldBlueprintIds: [Int]) {
        exportFieldBlueprints(fieldBlueprintIds: $fieldBlueprintIds) {
            jobId
        }
    }
    """

    def __init__(self, field_blueprint_ids: "Optional[List[int]]" = None):
        super().__init__(
            self.query,
            variables={"fieldBlueprintIds": field_blueprint_ids},
        )

    def process_response(self, response: "Payload") -> "Job":
        job_id = super().parse_payload(response)["exportFieldBlueprints"]["jobId"]
        return Job(id=job_id)


class ExportFieldBlueprints(RequestChain["Job"]):
    """
    Export field blueprints.

    Args:
        field_blueprint_ids (List[int], optional): List of field blueprint IDs to export.
            If not provided, exports all blueprints.
        wait (bool, optional): Wait for the export job to complete. Defaults to True.

    Returns:
        Job: The export job. Its `result["download_url"]` is a `/storage/...` path;
            fetch the export with `DownloadFieldBlueprintExport`.
    """

    def __init__(
        self,
        field_blueprint_ids: "Optional[List[int]]" = None,
        wait: bool = True,
    ):
        self.field_blueprint_ids = field_blueprint_ids
        self.wait = wait
        super().__init__()

    def requests(self) -> "Iterator[Union[_ExportFieldBlueprints, JobStatus]]":
        yield _ExportFieldBlueprints(field_blueprint_ids=self.field_blueprint_ids)
        if self.wait:
            yield JobStatus(id=self.previous.id, wait=True)


class _ImportFieldBlueprints(GraphQLRequest["Job"]):
    query = """
    mutation ImportFieldBlueprints($storageUri: String!) {
        importFieldBlueprints(storageUri: $storageUri) {
            jobId
        }
    }
    """

    def __init__(self, storage_uri: str):
        super().__init__(self.query, variables={"storageUri": storage_uri})

    def process_response(self, response: "Payload") -> "Job":
        job_id = super().parse_payload(response)["importFieldBlueprints"]["jobId"]
        return Job(id=job_id)


class ImportFieldBlueprints(RequestChain["Job"]):
    """
    Import field blueprints.

    Args:
        storage_uri (str): URI of the file to import.
        wait (bool, optional): Wait for the import job to complete. Defaults to True.

    Returns:
        Job: The import job
    """

    def __init__(self, storage_uri: str, wait: bool = True):
        self.storage_uri = storage_uri
        self.wait = wait
        super().__init__()

    def requests(self) -> "Iterator[Union[_ImportFieldBlueprints, JobStatus]]":
        yield _ImportFieldBlueprints(storage_uri=self.storage_uri)
        if self.wait:
            yield JobStatus(id=self.previous.id, wait=True)


class _GetFieldBlueprintImportUpload(GraphQLRequest["ExportUpload"]):
    query = """
    mutation GetImportUploadSignedUrl {
        getImportUploadSignedUrl {
            uploadUrl
            storageUri
        }
    }
    """

    def __init__(self) -> None:
        super().__init__(self.query)

    def process_response(self, response: "Payload") -> ExportUpload:
        return parse_export_upload(
            super().parse_payload(response)["getImportUploadSignedUrl"],
            "field blueprint import",
        )


class UploadFieldBlueprints(RequestChain["Union[Job, str]"]):
    """
    Upload a field blueprint import file through the authenticated client session.

    Args:
        file_path (str): path to the JSON file of blueprints, e.g. one fetched with
            `DownloadFieldBlueprintExport`.
        auto_import (bool, optional): import the uploaded file with `ImportFieldBlueprints`. Defaults to False.
        wait (bool, optional): with `auto_import`, wait for the import job to complete. Defaults to True.

    Returns:
        str: the storage uri of the uploaded file, or with `auto_import` the import Job.

    Raises:
        IndicoRequestError: if the platform returns no `/storage/` upload path, the upload
            is redirected, or the waited import job status is FAILURE.
    """

    def __init__(self, file_path: str, auto_import: bool = False, wait: bool = True):
        self.file_path = file_path
        self.auto_import = auto_import
        self.wait = wait
        super().__init__()

    def requests(
        self,
    ) -> "Iterator[Union[_GetFieldBlueprintImportUpload, ProxiedUpload, ImportFieldBlueprints]]":
        yield _GetFieldBlueprintImportUpload()
        upload: ExportUpload = self.previous

        yield ProxiedUpload(upload, self.file_path)

        if not self.auto_import:
            self.result = upload.storage_uri
            return

        yield ImportFieldBlueprints(storage_uri=upload.storage_uri, wait=self.wait)
        job: Job = self.previous
        if getattr(job, "status", None) == "FAILURE":
            result = getattr(job, "result", None)
            message = result.get("message") if isinstance(result, dict) else None
            detail = f": {message}" if message else ""
            raise IndicoRequestError(
                code="FAILURE",
                error=f"Failed to import field blueprints{detail}",
            )


class DownloadFieldBlueprintExport(RequestChain["Any"]):
    """
    Download a finished field blueprint export through the authenticated client session.

    Args:
        job (Job): the finished job from `ExportFieldBlueprints(wait=True)`.

    Returns:
        dict: the parsed export file.

    Raises:
        IndicoRequestError: if the job did not succeed, its `download_url` is not a
            `/storage/` path, or the download is redirected.
        IndicoInputError: if the job result has no `download_url`.
    """

    def __init__(self, job: Job):
        self.job = job
        super().__init__()

    def requests(self) -> "Iterator[RetrieveStorageObject]":
        if getattr(self.job, "status", None) != "SUCCESS":
            raise IndicoRequestError(
                code=400,
                error="The field blueprint export job must reach SUCCESS before it can be downloaded",
            )

        result = getattr(self.job, "result", None)
        download_url = result.get("download_url") if isinstance(result, dict) else None
        if not download_url:
            raise IndicoInputError(
                "The field blueprint export job result has no download_url; "
                "pass the job from ExportFieldBlueprints(wait=True)"
            )

        yield RetrieveStorageObject(
            storage_path(download_url), allow_redirects=False, timeout=None
        )
