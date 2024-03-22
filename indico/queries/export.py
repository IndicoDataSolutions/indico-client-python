import io
import warnings
from typing import List, Union

import pandas as pd

from indico.client import Delay, GraphQLRequest, RequestChain
from indico.errors import IndicoNotFound, IndicoRequestError
from indico.queries.storage import RetrieveStorageObject
from indico.types.export import Export, LabelResolutionStrategy


class _CreateExport(GraphQLRequest):
    query = """
        mutation CreateExport(
            $datasetId: Int!,
            $labelsetId: Int!,
            $columnIds: [Int],
            $modelIds: [Int],
            $frozenLabelsetIds: [Int],
            $combineLabels: LabelResolutionStrategy,
            $fileInfo: Boolean,
            $anonymous: Boolean
        ) {
            createExport(
                datasetId: $datasetId,
                labelsetId: $labelsetId,
                columnIds: $columnIds,
                modelIds: $modelIds,
                frozenLabelsetIds: $frozenLabelsetIds,
                combineLabels: $combineLabels,
                fileInfo: $fileInfo,
                anonymous: $anonymous
            ) {
                id,
                datasetId,
                labelsetId,
                name,
                status,
                columnIds,
                modelIds,
                frozenLabelsetIds,
                anonymous
                downloadUrl,
            }
        }

    """

    def __init__(
        self,
        dataset_id: int,
        labelset_id: int,
        column_ids: List[int] = None,
        model_ids: List[int] = None,
        frozen_labelset_ids: List[int] = None,
        combine_labels: LabelResolutionStrategy = LabelResolutionStrategy.ALL.name,
        file_info: bool = None,
        anonymoous: bool = None,
        anonymous: bool = None,
    ):
        if anonymoous:
            warnings.warn(
                "Argument anonymoous is deprecated and will be removed in future versions. Use argument anonymous instead."
            )
            if anonymous:
                raise IndicoRequestError("Cannot use both anonymoous and anonymous.")
            else:
                anonymous = anonymoous
        super().__init__(
            self.query,
            variables={
                "datasetId": dataset_id,
                "labelsetId": labelset_id,
                "columnIds": column_ids,
                "modelIds": model_ids,
                "frozenLabelsetIds": frozen_labelset_ids,
                "combineLabels": combine_labels,
                "fileInfo": file_info,
                "anonymous": anonymous,
            },
        )

    def process_response(self, response):
        response = super().process_response(response)
        return Export(**response["createExport"])


class GetExport(GraphQLRequest):
    """
    Get information on an Export job

    Args:
        export_id (int): Id of an Export

    Returns:
        Export object

    """

    query = """
        query GetExportStatus($exportIds: [Int]) {
            exports (exportIds: $exportIds) {
                exports {
                id
                datasetId
                name
                status
                columnIds
                labelsetId
                modelIds
                frozenLabelsetIds
                numLabels
                anonymous
                downloadUrl
                createdAt
                }
            }
        }
    """

    def __init__(self, export_id: int):
        super().__init__(self.query, variables={"exportIds": [export_id]})

    def process_response(self, response):
        response = super().process_response(response)
        return Export(**response["exports"]["exports"][0])


class _RetrieveExport(RetrieveStorageObject):
    def process_response(self, response):
        response = super().process_response(response)
        return pd.read_csv(io.StringIO(response))


class DownloadExport(RequestChain):
    """
    Download an export from an Indico storage url

    Args:
        export (Export): Export object
        export_id (int): Export id

    Returns:
        Pandas csv of the export

    Raises:
        IndicoRequestError if the Export job is not complete or failed
    """

    def __init__(self, export_id: int = None, export: Export = None):
        if not export_id and not export:
            raise IndicoRequestError(
                code="FAILURE",
                error="Please provide at least one of <export_id> or <export>",
            )
        self.export_id = export_id
        self.export = export

    def requests(self):
        if self.export_id:
            yield GetExport(self.export_id)
        export = self.export or self.previous

        if export.status != "COMPLETE":
            raise IndicoRequestError(
                code="400",
                error="The export must be complete and not failed before it can be downloaded",
            )

        yield _RetrieveExport(export.download_url)


class CreateExport(RequestChain):
    """
    Create an export job for a dataset.

    Args:
        dataset_id (int): Dataset to create the export for.
        labelset_id (int): Labelset column id to export.
        column_ids (List(int), optional): Data column ids to export. Defaults to None.
        model_ids (List(int), optional): Model ids to include predictions from. Defaults to None.
        frozen_labelset_ids: (List(int), optional): frozen labelset ids to limit examples by. Defaults to None.
        combine_labels (LabelResolutionStrategy, optional): One row per example, combine labels from multiple labels into a single row. Defaults to 'all'.
        file_info (bool, optional): Include datafile information. Defaults to False.
        anonymous (bool, optional): Anonymize user information. Defaults to False.
        wait (bool, optional): Wait for the export to complete. Defaults to True.
        request_interval (int or float, optional): The maximum time in between retry calls when waiting. Defaults to 5 seconds.

    Returns:
        Export object

    """

    previous = None

    def __init__(
        self,
        dataset_id: int,
        labelset_id: int,
        column_ids: List[int] = None,
        model_ids: List[int] = None,
        frozen_labelset_ids: List[int] = None,
        combine_labels: LabelResolutionStrategy = LabelResolutionStrategy.ALL.name,
        file_info: bool = False,
        anonymous: bool = False,
        wait: bool = True,
        request_interval: Union[int, float] = 5,
    ):
        self.dataset_id = dataset_id
        self.labelset_id = labelset_id
        self.column_ids = column_ids
        self.model_ids = model_ids
        self.frozen_labelset_ids = frozen_labelset_ids
        self.combine_labels = combine_labels
        self.file_info = file_info
        self.anonymous = anonymous
        self.wait = wait
        self.request_interval = request_interval
        super().__init__()

    def requests(self):
        yield _CreateExport(
            dataset_id=self.dataset_id,
            labelset_id=self.labelset_id,
            column_ids=self.column_ids,
            model_ids=self.model_ids,
            frozen_labelset_ids=self.frozen_labelset_ids,
            combine_labels=self.combine_labels,
            file_info=self.file_info,
            anonymous=self.anonymous,
        )
        if self.wait is True:
            while self.previous.status not in ["COMPLETE", "FAILED"]:
                yield GetExport(self.previous.id)
                yield Delay(seconds=self.request_interval)

        yield GetExport(self.previous.id)
