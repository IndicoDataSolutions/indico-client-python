import re
import tomllib
from pathlib import Path


def _load_release_pattern() -> str:
    pyproject_path = Path(__file__).resolve().parents[2] / "pyproject.toml"
    with pyproject_path.open("rb") as f:
        pyproject = tomllib.load(f)
    return pyproject["tool"]["uv-dynamic-versioning"]["pattern"]


def test_release_pattern_matches_standard_tag() -> None:
    pattern = re.compile(_load_release_pattern())
    match = pattern.match("7.9.0")
    assert match is not None
    assert match.groupdict() == {"base": "7.9.0", "stage": None, "revision": None}


def test_release_pattern_matches_hyphen_prerelease_tag() -> None:
    pattern = re.compile(_load_release_pattern())
    match = pattern.match("7.9.0-rc1")
    assert match is not None
    assert match.groupdict() == {"base": "7.9.0", "stage": "rc", "revision": "1"}


def test_release_pattern_matches_post_release_tag() -> None:
    pattern = re.compile(_load_release_pattern())
    match = pattern.match("7.9.0.post1")
    assert match is not None
    assert match.groupdict() == {"base": "7.9.0", "stage": "post", "revision": "1"}
