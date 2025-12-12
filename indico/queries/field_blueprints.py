from typing import TYPE_CHECKING

from indico.client.request import (
    GraphQLRequest,
    PagedRequestV2,
    RequestChain,
)
from indico.queries.jobs import JobStatus
from indico.types.field_blueprint import FieldBlueprint
from indico.types.jobs import Job

if TYPE_CHECKING:  # pragma: no cover
    from typing import Iterator, List, Optional, Union

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
                }
                ... on ClassificationFieldConfig {
                name
                datatype
                targetNames
                }
            }
            promptConfig {
                ... on ExtractionPromptConfig {
                prompt
                targetName
                multipleValues
                minimumLocationType
                localization
                }
                ... on ClassificationPromptConfig {
                globalPrompt
                targetNames {
                    prompt
                    targetName
                }
                }
                ... on SummarizationPromptConfig {
                prompt
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
                            name
                            datatype
                            required
                            multiple
                            validationConfig {
                                settingName
                                settingValue
                                onFailure
                            }
                            formatConfig
                            inputConfig
                        }
                        ... on ClassificationFieldConfig {
                            name
                            datatype
                            targetNames
                        }
                    }
                    promptConfig {
                        ... on ExtractionPromptConfig {
                            prompt
                            localization
                            targetName
                            multipleValues
                            minimumLocationType
                        }
                        ... on ClassificationPromptConfig {
                            globalPrompt
                            targetNames {
                                prompt
                                targetName
                            }
                        }
                        ... on SummarizationPromptConfig {
                            prompt
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

    Options:
        limit (int, default=100): Max number of blueprints to retrieve per page

    Returns:
        List[FieldBlueprint]
    """

    query = """
    query ListFieldBlueprints($size: Int, $cursor: String, $filters: [ColumnFilterInput]) {
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
                                name
                                datatype
                                required
                                multiple
                                validationConfig {
                                    settingName
                                    settingValue
                                    onFailure
                                }
                                formatConfig
                                inputConfig
                            }
                            ... on ClassificationFieldConfig {
                                name
                                datatype
                                targetNames
                            }
                        }
                        promptConfig {
                            ... on ExtractionPromptConfig {
                                prompt
                                localization
                                targetName
                                multipleValues
                                minimumLocationType
                            }
                            ... on ClassificationPromptConfig {
                                globalPrompt
                                targetNames {
                                    prompt
                                    targetName
                                }
                            }
                            ... on SummarizationPromptConfig {
                                prompt
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

    def __init__(self, limit: int = 100, filters: "Optional[List[AnyDict]]" = None):
        super().__init__(self.query, variables={"limit": limit, "filters": filters})

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
        Job: The export job
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
