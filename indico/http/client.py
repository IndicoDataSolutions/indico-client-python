import asyncio
import logging
from contextlib import contextmanager
from copy import deepcopy
from http.cookiejar import DefaultCookiePolicy
from pathlib import Path
from typing import TYPE_CHECKING, cast

import niquests

from indico.config import IndicoConfig
from indico.errors import (
    IndicoAuthenticationFailed,
    IndicoHibernationError,
    IndicoRequestError,
)
from indico.http.serialization import aio_deserialize, deserialize

from .retry import aioretry

if TYPE_CHECKING:  # pragma: no cover
    from http.cookiejar import Cookie
    from io import IOBase
    from typing import Any, Dict, Iterator, List, Optional, Union
    from urllib.request import Request

    from indico.client.request import HTTPRequest, ResponseType
    from indico.typing import AnyDict


logger = logging.getLogger(__file__)


class CookiePolicyOverride(DefaultCookiePolicy):
    def set_ok(self, cookie: "Cookie", request: "Request") -> bool:
        return True

    def return_ok(self, cookie: "Cookie", request: "Request") -> bool:
        return True

    def path_return_ok(self, path: str, request: "Request") -> bool:
        return True

    def domain_return_ok(self, domain: str, request: "Request") -> bool:
        return True


class HTTPClient:
    def __init__(self, config: "Optional[IndicoConfig]" = None):
        self.config = config or IndicoConfig()
        self.base_url = f"{self.config.protocol}://{self.config.host}"

        self.request_session = niquests.Session()
        if isinstance(self.config.requests_params, dict):
            for param in self.config.requests_params.keys():
                setattr(self.request_session, param, self.config.requests_params[param])
        self.request_session.cookies.set_policy(CookiePolicyOverride())

        self.get_short_lived_access_token()

    def post(
        self,
        *args: "Any",
        json: "Optional[Union[AnyDict, List[Any]]]" = None,
        **kwargs: "Any",
    ) -> "Any":
        return self._make_request("post", *args, json=json, **kwargs)

    def get(
        self, *args: "Any", params: "Optional[AnyDict]" = None, **kwargs: "Any"
    ) -> "Any":
        return self._make_request("post", *args, params=params, **kwargs)

    def get_short_lived_access_token(self) -> "AnyDict":
        if "auth_token" in self.request_session.cookies:
            self.request_session.cookies.pop("auth_token")

        r = self.post(
            "/auth/users/refresh_token",
            headers={"Authorization": f"Bearer {self.config.api_token}"},
            _refreshed=True,
        )

        if self.config._disable_cookie_domain:
            value = self.request_session.cookies.get("auth_token", None)
            if not value:
                raise IndicoAuthenticationFailed()
            self.request_session.cookies.pop("auth_token")
            self.request_session.cookies.set_cookie(
                niquests.cookies.create_cookie(name="auth_token", value=value)  # type: ignore
            )

        return cast("AnyDict", r)

    def execute_request(self, request: "HTTPRequest[ResponseType]") -> "ResponseType":
        return request.process_response(
            self._make_request(
                method=request.method.value.lower(), path=request.path, **request.kwargs
            )
        )

    @contextmanager
    def _handle_files(self, req_kwargs: "AnyDict") -> "Iterator[AnyDict]":
        streams = None
        if "streams" in req_kwargs:
            if req_kwargs["streams"] is not None:
                streams = req_kwargs["streams"].copy()
            del req_kwargs["streams"]

        new_kwargs: "AnyDict" = deepcopy(req_kwargs)

        files: "List[IOBase]" = []
        file_arg = {}
        dup_counts: "Dict[str, int]" = {}
        if "files" in new_kwargs and new_kwargs["files"] is not None:
            for filepath in new_kwargs["files"]:
                path = Path(filepath)
                fd = path.open("rb")
                files.append(fd)
                if path.stem in dup_counts:
                    file_arg[path.stem + f"({dup_counts[path.stem]})"] = fd
                    dup_counts[path.stem] += 1
                else:
                    file_arg[path.stem] = fd
                    dup_counts[path.stem] = 1

        if streams is not None and len(streams) > 0:
            for filename in streams:
                stream = streams[filename]
                files.append(stream)
                if filename in dup_counts:
                    file_arg[filename + f"({dup_counts[filename]})"] = stream
                    dup_counts[filename] += 1
                else:
                    file_arg[filename] = stream
                    dup_counts[filename] = 1

        new_kwargs["files"] = file_arg

        try:
            yield new_kwargs
        finally:
            for f in files:
                f.close()

    def _make_request(
        self,
        method: str,
        path: str,
        headers: "Optional[Dict[str, str]]" = None,
        _refreshed: bool = False,
        **request_kwargs: "Any",
    ) -> "Any":
        logger.debug(
            f"[{method}] {path}\n\t Headers: {headers}\n\tRequest Args:{request_kwargs}"
        )
        with self._handle_files(request_kwargs) as new_kwargs:
            response = getattr(self.request_session, method)(
                f"{self.base_url}{path}",
                headers=headers,
                stream=True,
                verify=False
                if not self.config.verify_ssl or not self.request_session.verify
                else True,
                **new_kwargs,
            )

        json: bool = ".json" in Path(path).suffixes
        decompress: bool = Path(path).suffix == ".gz"

        if response.status_code == 401 and not _refreshed:
            self.get_short_lived_access_token()
            return self._make_request(
                method, path, headers, _refreshed=True, **request_kwargs
            )
        elif response.status_code == 401 and _refreshed:
            raise IndicoAuthenticationFailed()

        if response.status_code == 503 and "Retry-After" in response.headers:
            raise IndicoHibernationError(after=response.headers.get("Retry-After"))

        if response.status_code >= 500:
            raise IndicoRequestError(
                code=response.status_code,
                error=response.reason,
                extras=repr(response.content),
            )

        content: "Any" = deserialize(
            response, force_json=json, force_decompress=decompress
        )

        if response.status_code >= 400:
            if isinstance(content, dict):
                error = (
                    f"{content.pop('error_type', 'Unknown Error')}, "
                    f"{content.pop('message', '')}"
                )
                extras = content
            else:
                error = content
                extras = None

            raise IndicoRequestError(
                error=error, code=response.status_code, extras=extras
            )

        return content


class AIOHTTPClient:
    """
    Async client using niquests. Supports HTTP/1.1 and HTTP/2.
    """

    def __init__(self, config: "Optional[IndicoConfig]" = None):
        self.config = config or IndicoConfig()
        self.base_url = f"{self.config.protocol}://{self.config.host}"

        self.request_session = niquests.AsyncSession()
        self.request_session.verify = self.config.verify_ssl
        if isinstance(self.config.requests_params, dict):
            for param in self.config.requests_params.keys():
                setattr(self.request_session, param, self.config.requests_params[param])

    async def post(
        self,
        *args: "Any",
        json: "Optional[Union[AnyDict, List[Any]]]" = None,
        **kwargs: "Any",
    ) -> "Any":
        return await self._make_request("post", *args, json=json, **kwargs)

    async def get(
        self, *args: "Any", params: "Optional[AnyDict]" = None, **kwargs: "Any"
    ) -> "Any":
        return await self._make_request("post", *args, params=params, **kwargs)

    async def get_short_lived_access_token(self) -> "AnyDict":
        r = await self.post(
            "/auth/users/refresh_token",
            headers={"Authorization": f"Bearer {self.config.api_token}"},
            _refreshed=True,
        )
        return cast("AnyDict", r)

    async def execute_request(
        self, request: "HTTPRequest[ResponseType]"
    ) -> "ResponseType":
        return request.process_response(
            await self._make_request(
                method=request.method.value.lower(), path=request.path, **request.kwargs
            )
        )

    @contextmanager
    def _handle_files(self, req_kwargs: "AnyDict") -> "Iterator[List[Dict[str, Any]]]":
        files: "List[Any]" = []
        file_args: "List[Dict[str, Any]]" = []
        dup_counts: "Dict[str, int]" = {}
        for filepath in req_kwargs.pop("files", []) or []:
            path = Path(filepath)
            fd = path.open("rb")
            files.append(fd)
            _add_suffix = f".{path.suffix}" if path.suffix else ""
            if path.stem in dup_counts:
                name = path.stem + f"({dup_counts[path.stem]})" + _add_suffix
                dup_counts[path.stem] += 1
            else:
                name = path.name
                dup_counts[path.stem] = 1
            file_args.append({"files": {"file": (name, fd)}})

        for filename, stream in (req_kwargs.pop("streams", {}) or {}).items():
            files.append(stream)
            if filename in dup_counts:
                name = filename + f"({dup_counts[filename]})"
                dup_counts[filename] += 1
            else:
                name = filename
                dup_counts[filename] = 1
            file_args.append({"files": {"file": (name, stream)}})

        try:
            yield file_args
        finally:
            for f in files:
                f.close()

    @aioretry(niquests.ConnectionError)
    async def _make_request(
        self,
        method: str,
        path: str,
        headers: "Optional[Dict[str, str]]" = None,
        _refreshed: bool = False,
        **request_kwargs: "Any",
    ) -> "Any":
        logger.debug(
            f"[{method}] {path}\n\t Headers: {headers}\n\tRequest Args:{request_kwargs}"
        )
        json: bool = ".json" in Path(path).suffixes
        decompress: bool = Path(path).suffix == ".gz"

        with self._handle_files(request_kwargs) as file_args:
            if file_args:
                resps = await asyncio.gather(
                    *(
                        self._make_request(
                            method, path, headers, **request_kwargs, **data
                        )
                        for data in file_args
                    )
                )
                return [resp for resp_set in resps for resp in resp_set]

            response: niquests.Response = await getattr(self.request_session, method)(
                f"{self.base_url}{path}",
                headers=headers,
                **request_kwargs,
            )

            if response.status_code == 401 and not _refreshed:
                await self.get_short_lived_access_token()
                return await self._make_request(
                    method, path, headers, _refreshed=True, **request_kwargs
                )
            if response.status_code == 401 and _refreshed:
                raise IndicoAuthenticationFailed()

            if response.status_code == 503 and "Retry-After" in response.headers:
                raise IndicoHibernationError(after=response.headers.get("Retry-After"))

            if response.status_code >= 500:
                raise IndicoRequestError(
                    code=response.status_code,
                    error=response.reason or "",
                    extras=repr(response.content),
                )

            content: "Any" = await aio_deserialize(
                response, force_json=json, force_decompress=decompress
            )

            if response.status_code >= 400:
                if isinstance(content, dict):
                    error = (
                        f"{content.pop('error_type', 'Unknown Error')}, "
                        f"{content.pop('message', '')}"
                    )
                    extras = content
                else:
                    error = content
                    extras = None

                raise IndicoRequestError(
                    error=error, code=response.status_code, extras=extras
                )

            return content
