import pandas as pd
import io
from typing import List, Union

from indico.client import GraphQLRequest, RequestChain, Debouncer
from indico.errors import IndicoNotFound, IndicoRequestError
from indico.types.export import Export
from indico.queries.storage import RetrieveStorageObject


class _CreateExport(GraphQLRequest):
    query = """
        mutation CreateExport(
            $datasetId: Int!, 
            $columnIds: [Int], 
            $subsetIds: [Int], 
            $labelsetIds: [Int],
            $fileInfo: Boolean,
            $combineLabels: Boolean,
            $anonymous: Boolean
        ) {
            createExport(
                datasetId: $datasetId,
                columnIds: $columnIds,
                subsetIds: $subsetIds,
                fileInfo: $fileInfo,
                labelsetIds: $labelsetIds,
                combineLabels: $combineLabels
                anonymous: $anonymous
            ) {
                id,
                datasetId,
                name,
                status,
                downloadUrl,
                columnIds,
                labelsetIds,
                subsetIds
            }
        }    

    """

    def __init__(
        self,
        dataset_id: int,
        column_ids: List[int] = None,
        subset_ids: List[int] = None,
        labelset_ids: List[int] = None,
        file_info: bool = None,
        combine_labels: bool = None,
        anonymoous: bool = None,
    ):
        super().__init__(
            self.query,
            variables={
                "datasetId": dataset_id,
                "columnIds": column_ids,
                "subsetIds": subset_ids,
                "labelsetIds": labelset_ids,
                "fileInfo": file_info,
                "combineLabels": combine_labels,
                "anonymous": anonymoous,
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
                labelsetIds
                subsetIds
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
        dataset_id (int): Dataset to create the export for
        subset_ids: (List(int)): Subset ids to export rows sets
        column_ids (List(int)): Data column ids to export
        labelset_ids: (List(int)): Labelset column ids to export
        file_info: (bool): Include datafile information
        combine_labels: (bool): One row per example, combine labels from multiple labels into a single row
        anonymous: (bool): Anonymize user information
        wait: (bool): Wait for the export to complete. Default is True

    Returns:
        Export object

    """

    previous = None

    def __init__(
        self,
        dataset_id: int,
        subset_ids: List[int] = None,
        column_ids: List[int] = None,
        labelset_ids: List[int] = None,
        file_info: bool = False,
        combine_labels: bool = False,
        anonymous: bool = False,
        wait: bool = True,
    ):
        self.dataset_id = dataset_id
        self.column_ids = column_ids
        self.subset_ids = subset_ids
        self.labelset_ids = labelset_ids
        self.file_info = file_info
        self.combine_labels = combine_labels
        self.anonymous = anonymous
        self.wait = wait
        super().__init__()

    def requests(self):
        yield _CreateExport(
            dataset_id=self.dataset_id,
            column_ids=self.column_ids,
            subset_ids=self.subset_ids,
            labelset_ids=self.labelset_ids,
            file_info=self.file_info,
            combine_labels=self.combine_labels,
            anonymoous=self.anonymous,
        )
        debouncer = Debouncer()
        if self.wait is True:
            while self.previous.status not in ["COMPLETE", "FAILED"]:
                yield GetExport(self.previous.id)
                debouncer.backoff()

        yield GetExport(self.previous.id)
