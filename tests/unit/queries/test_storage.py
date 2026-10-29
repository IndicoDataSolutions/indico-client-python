import pytest

from indico.errors import IndicoRequestError
from indico.queries.storage import RetrieveStorageObject, storage_path


@pytest.mark.parametrize(
    "url, expected",
    [
        (
            "https://rainbow.example/storage/static_uploads/upload?name=a.indico",
            "/storage/static_uploads/upload?name=a.indico",
        ),
        (
            "https://elsewhere/storage/static_uploads/upload?name=a.indico",
            "/storage/static_uploads/upload?name=a.indico",
        ),
        ("https://h/storage/exports/a.zip", "/storage/exports/a.zip"),
        ("https://h/storage/exports/a.zip?", "/storage/exports/a.zip"),
        ("/storage/x", "/storage/x"),
        ("/storage/a..b/x", "/storage/a..b/x"),
    ],
)
def test_storage_path(url: str, expected: str) -> None:
    assert storage_path(url) == expected


@pytest.mark.parametrize(
    "url",
    [
        "/not-storage/x",
        "https://h/",
        "https://h/storagex/y",
        "/storage/../auth/users",
        "/storage/a/../../auth",
        "/storage/a/../b",
        "/storage/./x",
        "/storage/%2e%2e/auth",
        "/storage/%2E%2E/auth",
        "https://h/storage/a/%2e%2e/%2e%2e/auth?name=x",
        "/storage/.%2e/auth",
        "/storage/a/%2e%2e/b",
        "/storage/%2e/x",
        "/storage/",
        "https://h/storage/?name=x",
        "/%73torage/x",
    ],
)
def test_storage_path_rejects(url: str) -> None:
    with pytest.raises(IndicoRequestError):
        storage_path(url)


@pytest.mark.parametrize("allow_redirects", [True, False])
def test_retrieve_storage_object_forwards_allow_redirects(
    allow_redirects: bool,
) -> None:
    request = RetrieveStorageObject(
        "/storage/x", raw_response=True, allow_redirects=allow_redirects
    )
    assert request.kwargs == {"allow_redirects": allow_redirects}
    assert request.raw_response is True
