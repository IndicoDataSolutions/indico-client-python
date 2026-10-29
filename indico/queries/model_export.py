import warnings
from typing import TYPE_CHECKING, cast

from indico.client.request import Delay, GraphQLRequest, RequestChain
from indico.errors import IndicoInputError, IndicoRequestError
from indico.queries.storage import RetrieveStorageObject, storage_path
from indico.types.model_export import ModelExport

if TYPE_CHECKING:  # pragma: no cover
    from typing import Any, Iterator, List, Optional, Union

    from indico.typing import Payload

__all__ = [
    "CreateModelExport",
    "DownloadModelExport",
    "GetModelExports",
    "ModelExport",
]


class _CreateModelExport(GraphQLRequest["ModelExport"]):
    query = """
        mutation ($modelId: Int!) {
            createModelExport(
                modelId: $modelId
            ) {
                id
                name
                status
                modelId
            }
        }
    """

    def __init__(self, model_id: int):
        self.model_id = model_id
        super().__init__(self.query, variables={"modelId": model_id})

    def process_response(self, response: "Payload") -> ModelExport:
        return ModelExport(**super().parse_payload(response)["createModelExport"])


class CreateModelExport(RequestChain["List[ModelExport]"]):
    """
    Create a model export.

    Available on 6.14+ only.

    Args:
        model_id (int): the model id.
        wait (bool): wait for the export to complete and fetch its `download_url`. Defaults to True.
        request_interval (int | float): the interval between requests in seconds. Defaults to 5.
    """

    previous: "Any" = None

    def __init__(
        self,
        model_id: int,
        wait: bool = True,
        request_interval: "Union[int, float]" = 5,
    ):
        self.wait = wait
        self.model_id = model_id
        self.request_interval = request_interval
        super().__init__()

    def requests(self) -> "Iterator[Union[_CreateModelExport, Delay, GetModelExports]]":
        yield _CreateModelExport(self.model_id)
        if self.wait:
            while self.previous and self.previous.status not in ["COMPLETE", "FAILED"]:
                yield GetModelExports([self.previous.id])
                self.previous = self.previous[0]
                yield Delay(seconds=self.request_interval)

        yield GetModelExports([self.previous.id], with_download_url=self.wait is True)


class GetModelExports(GraphQLRequest["List[ModelExport]"]):
    """
    Get model export(s).

    Available on 6.14+ only.

    Args:
        export_ids (list[int]): the export ids.
        with_download_url (bool): include `download_url`. Defaults to False
        with_signed_url (bool): deprecated alias of `with_download_url`; `signed_url` is always None. Defaults to False
    """

    query = """
        query getModelExports($exportIds: [Int]) {
            modelExports(exportIds: $exportIds) {
                modelExports {
                    {fields}
                }
            }
        }
    """

    _base_fields = [
        "id",
        "name",
        "status",
        "modelId",
        "filePath",
        "createdAt",
        "createdBy",
    ]

    def __init__(
        self,
        export_ids: "List[int]",
        with_download_url: bool = False,
        with_signed_url: bool = False,
    ):
        if with_signed_url:
            warnings.warn(
                "`with_signed_url` is deprecated; use `with_download_url` "
                "or `DownloadModelExport` instead",
                DeprecationWarning,
                stacklevel=2,
            )
        url_fields = ["downloadUrl"] if with_download_url or with_signed_url else []
        fields = [*self._base_fields, *url_fields]

        query_with_fields = self.query.replace("{fields}", "\n".join(fields))
        super().__init__(query_with_fields, variables={"exportIds": export_ids})

    def process_response(self, response: "Payload") -> "List[ModelExport]":
        return [
            ModelExport(**export)
            for export in super().parse_payload(response)["modelExports"][
                "modelExports"
            ]
        ]


class DownloadModelExport(RequestChain[bytes]):
    """
    Download a completed model export through the authenticated client session.

    Pass exactly one of `export_id` (refetched for a fresh download url) or `export`.
    The whole export is held in memory.

    Args:
        export_id (int): the model export id.
        export (ModelExport): a model export from `CreateModelExport(wait=True)` or
            `GetModelExports(with_download_url=True)`.

    Returns:
        bytes: the export file contents.

    Raises:
        IndicoInputError: if not exactly one of `export_id` or `export` is given,
            or `export` has no `download_url`.
        IndicoRequestError: if the export is unknown, not complete, or the download is redirected.
    """

    def __init__(
        self,
        export_id: "Optional[int]" = None,
        export: "Optional[ModelExport]" = None,
    ):
        if (export_id is None) == (export is None):
            raise IndicoInputError(
                "Please provide exactly one of <export_id> or <export>"
            )
        self.export_id = export_id
        self.export = export

    def requests(self) -> "Iterator[Union[GetModelExports, RetrieveStorageObject]]":
        if self.export_id is not None:
            yield GetModelExports([self.export_id], with_download_url=True)
            if not self.previous:
                raise IndicoRequestError(
                    code=404, error=f"Model export {self.export_id} not found"
                )
            self.export = self.previous[0]

        export = cast(ModelExport, self.export)
        if export.status != "COMPLETE":
            raise IndicoRequestError(
                code=400,
                error="The model export must be complete before it can be downloaded",
            )

        download_url: "Optional[str]" = getattr(export, "download_url", None)
        if not download_url:
            raise IndicoInputError(
                "The model export has no download_url; fetch it with "
                "GetModelExports(with_download_url=True) or pass export_id"
            )

        yield RetrieveStorageObject(
            storage_path(download_url), raw_response=True, allow_redirects=False
        )
        self.result = self.previous
