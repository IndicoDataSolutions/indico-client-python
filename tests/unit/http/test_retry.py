import pytest

from indico.http.retry import retry


def test_no_errors() -> None:
    @retry(Exception, count=0, wait=0, backoff=0, jitter=0)
    def no_errors() -> bool:
        return True

    assert no_errors()


def test_raises_errors() -> None:
    calls = 0

    @retry(RuntimeError, count=4, wait=0, backoff=0, jitter=0)
    def raises_errors() -> None:
        nonlocal calls
        calls += 1
        raise RuntimeError()

    with pytest.raises(RuntimeError):
        raises_errors()

    assert calls == 5


def test_raises_other_errors() -> None:
    calls = 0

    @retry(RuntimeError, count=4, wait=0, backoff=0, jitter=0)
    def raises_errors() -> None:
        nonlocal calls
        calls += 1
        raise ValueError()

    with pytest.raises(ValueError):
        raises_errors()

    assert calls == 1


@pytest.mark.asyncio
async def test_raises_errors_async() -> None:
    calls = 0

    @retry(RuntimeError, count=4, wait=0, backoff=0, jitter=0)
    async def raises_errors() -> None:
        nonlocal calls
        calls += 1
        raise RuntimeError()

    with pytest.raises(RuntimeError):
        await raises_errors()

    assert calls == 5


@pytest.mark.asyncio
async def test_raises_other_errors_async() -> None:
    calls = 0

    @retry(RuntimeError, count=4, wait=0, backoff=0, jitter=0)
    async def raises_errors() -> None:
        nonlocal calls
        calls += 1
        raise ValueError()

    with pytest.raises(ValueError):
        await raises_errors()

    assert calls == 1
