from typing import Any, Dict

import pytest

from indico.errors import IndicoRequestError
from indico.queries.storage import RetrieveStorageObject, storage_path


def test_storage_path() -> None:
    assert storage_path("/storage/a?name=b") == "/storage/a?name=b"


@pytest.mark.parametrize("url", ["https://h/storage/x", "/storagex/y", "@evil/x"])
def test_storage_path_rejects(url: str) -> None:
    with pytest.raises(IndicoRequestError):
        storage_path(url)


@pytest.mark.parametrize(
    "kwargs, expected",
    [
        ({}, {}),
        ({"timeout": None}, {"timeout": None}),
        ({"timeout": 5.0}, {"timeout": 5.0}),
    ],
)
def test_retrieve_storage_object_timeout_only_when_given(
    kwargs: Dict[str, Any], expected: Dict[str, Any]
) -> None:
    request_kwargs = RetrieveStorageObject("/storage/a", **kwargs).kwargs
    assert {k: v for k, v in request_kwargs.items() if k == "timeout"} == expected
