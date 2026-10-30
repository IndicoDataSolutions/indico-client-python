import pytest

from indico.errors import IndicoRequestError
from indico.queries.storage import storage_path


def test_storage_path() -> None:
    assert storage_path("/storage/a?name=b") == "/storage/a?name=b"


@pytest.mark.parametrize("url", ["https://h/storage/x", "/storagex/y", "@evil/x"])
def test_storage_path_rejects(url: str) -> None:
    with pytest.raises(IndicoRequestError):
        storage_path(url)
