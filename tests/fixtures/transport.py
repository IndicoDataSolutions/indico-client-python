from typing import Any, Callable, Dict, List, Optional, Sequence

import aiohttp

RequestMocker = Callable[..., Any]


class FakeAioCall:
    def __init__(self, method: str, url: str, kwargs: Dict[str, Any]):
        self.method = method
        self.url = url
        self.kwargs = kwargs
        self.body: Optional[bytes] = None


class FakeAioResponse:
    reason = "OK"

    def __init__(
        self,
        status: int = 200,
        body: bytes = b"",
        headers: Optional[Dict[str, str]] = None,
    ):
        self.status = status
        self.body = body
        self.content = body
        self.headers: Dict[str, str] = headers or {"Content-Type": "text/plain"}

    async def read(self) -> bytes:
        return self.body


class FakeAioRequest:
    """Send one queued exchange the way aiohttp does: write the body once, then close it."""

    def __init__(self, session: "FakeAioSession", call: FakeAioCall):
        self.session = session
        self.call = call

    async def __aenter__(self) -> FakeAioResponse:
        data = self.call.kwargs.get("data")
        if isinstance(data, aiohttp.FormData):
            payload = data()
            self.call.body = await payload.as_bytes()
            await payload.close()
        response = self.session.responses.pop(0)
        if 300 <= response.status < 400 and self.call.kwargs.get(
            "allow_redirects", True
        ):
            redirected = self.session.request(
                self.call.method, response.headers["Location"], **self.call.kwargs
            )
            return await redirected.__aenter__()
        return response

    async def __aexit__(self, *args: Any) -> None:
        return None


class FakeAioSession:
    """Answer aiohttp-style requests from a queue, following redirects unless `allow_redirects=False`."""

    def __init__(self, responses: Optional[Sequence[FakeAioResponse]] = None):
        self.responses: List[FakeAioResponse] = list(responses or [])
        self.calls: List[FakeAioCall] = []

    def request(self, method: str, url: str, **kwargs: Any) -> FakeAioRequest:
        call = FakeAioCall(method=method, url=url, kwargs=kwargs)
        self.calls.append(call)
        return FakeAioRequest(self, call)

    def get(self, url: str, **kwargs: Any) -> FakeAioRequest:
        return self.request("get", url, **kwargs)

    def post(self, url: str, **kwargs: Any) -> FakeAioRequest:
        return self.request("post", url, **kwargs)
