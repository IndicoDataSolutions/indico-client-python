import asyncio
import aiohttp
import http.cookiejar
import logging
from contextlib import contextmanager
from copy import deepcopy
from pathlib import Path
from typing import Union, Optional

import requests
from indico.client.request import HTTPRequest
from indico.config import IndicoConfig
from indico.errors import (
    IndicoAuthenticationFailed,
    IndicoRequestError,
    IndicoHibernationError,
)
from indico.http.serialization import deserialize, aio_deserialize
from .retry import aioretry

logger = logging.getLogger(__file__)


class CookiePolicyOverride(http.cookiejar.DefaultCookiePolicy):
    def set_ok(self, cookie, request):
        return True

    def return_ok(self, cookie, request):
        return True

    def path_return_ok(self, path, request):
        return True

    def domain_return_ok(self, domain, request):
        return True


class HTTPClient:
    def __init__(self, config: IndicoConfig = None):
        self.config = config
        self.base_url = f"{self.config.protocol}://{self.config.host}"

        self.request_session = requests.Session()
        if config and isinstance(config.requests_params, dict):
            for param in config.requests_params.keys():
                setattr(self.request_session, param, config.requests_params[param])
        self.request_session.cookies.set_policy(CookiePolicyOverride())
        self.get_short_lived_access_token()

    def post(self, *args, json: Union[dict, list] = None, **kwargs):
        return self._make_request("post", *args, json=json, **kwargs)

    def get(self, *args, params: dict = None, **kwargs):
        return self._make_request("post", *args, params=params, **kwargs)

    def get_short_lived_access_token(self):
        # If the cookie here is already due to _disable_cookie_domain set and we try to pop it later
        # it will error out because we have two cookies with the same name. We just remove the old one
        # here as we are about to refresh it.
        if "auth_token" in self.request_session.cookies:
            self.request_session.cookies.pop("auth_token")

        r = self.post(
            "/auth/users/refresh_token",
            headers={"Authorization": f"Bearer {self.config.api_token}"},
            _refreshed=True,
        )

        # Disable cookie domain in cases where the domain won't match due to using short name domains
        if self.config._disable_cookie_domain:
            value = self.request_session.cookies.get("auth_token", None)
            if not value:
                raise IndicoAuthenticationFailed()
            self.request_session.cookies.pop("auth_token")
            self.request_session.cookies.set_cookie(
                requests.cookies.create_cookie(name="auth_token", value=value)
            )

        return r

    def execute_request(self, request: HTTPRequest):
        return request.process_response(
            self._make_request(
                method=request.method.value.lower(), path=request.path, **request.kwargs
            )
        )

    @contextmanager
    def _handle_files(self, req_kwargs):

        streams = None
        # deepcopying buffers is not supported
        # so, remove "streams" before the deepcopy.
        if "streams" in req_kwargs:
            if req_kwargs["streams"] is not None:
                streams = req_kwargs["streams"].copy()
            del req_kwargs["streams"]

        new_kwargs = deepcopy(req_kwargs)

        files = []
        file_arg = {}
        dup_counts = {}
        if "files" in new_kwargs and new_kwargs["files"] is not None:
            for filepath in new_kwargs["files"]:
                path = Path(filepath)
                fd = path.open("rb")
                files.append(fd)
                # follow the convention of adding (n) after a duplicate filename
                if path.stem in dup_counts:
                    file_arg[path.stem + f"({dup_counts[path.stem]})"] = fd
                    dup_counts[path.stem] += 1
                else:
                    file_arg[path.stem] = fd
                    dup_counts[path.stem] = 1

        if streams is not None and len(streams) > 0:
            for filename in streams:
                # similar operation as above.
                stream = streams[filename]
                files.append(stream)
                if filename in dup_counts:
                    file_arg[filename + f"({dup_counts[filename]})"] = stream
                    dup_counts[filename] += 1
                else:
                    file_arg[filename] = stream
                    dup_counts[filename] = 1

        new_kwargs["files"] = file_arg

        yield new_kwargs

        if files:
            [f.close() for f in files]

    def _make_request(
        self,
        method: str,
        path: str,
        headers: dict = None,
        _refreshed=False,
        **request_kwargs,
    ):
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

        # If auth expired refresh
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

        content = deserialize(response, force_json=json, force_decompress=decompress)

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


class AIOHTTPClient(HTTPClient):
    """
    Beta client with a minimal set of features that can execute
    requests using the aiohttp library
    """

    def __init__(self, config: Optional[IndicoConfig] = None):
        """
        Config options specific to aiohttp
        unsafe - allows interacting with IP urls
        """
        self.config = config or IndicoConfig()
        self.base_url = f"{self.config.protocol}://{self.config.host}"
        unsafe = config.verify_ssl

        self.request_session = aiohttp.ClientSession()
        self.request_session.cookie_jar._unsafe = unsafe
        if config and isinstance(config.requests_params, dict):
            for param in config.requests_params.keys():
                setattr(self.request_session, param, config.requests_params[param])

    async def post(self, *args, json: Union[dict, list] = None, **kwargs):
        return await self._make_request("post", *args, json=json, **kwargs)

    async def get(self, *args, params: dict = None, **kwargs):
        return await self._make_request("post", *args, params=params, **kwargs)

    async def get_short_lived_access_token(self):
        r = await self.post(
            "/auth/users/refresh_token",
            headers={"Authorization": f"Bearer {self.config.api_token}"},
            _refreshed=True,
        )
        return r

    async def execute_request(self, request: HTTPRequest):
        return request.process_response(
            await self._make_request(
                method=request.method.value.lower(), path=request.path, **request.kwargs
            )
        )

    @contextmanager
    def _handle_files(self, req_kwargs):
        files = []
        file_args = []
        dup_counts = {}
        for filepath in req_kwargs.pop("files", []) or []:
            data = aiohttp.FormData()
            path = Path(filepath)
            fd = path.open("rb")
            files.append(fd)
            # follow the convention of adding (n) after a duplicate filename
            _add_suffix = f".{path.suffix}" if path.suffix else ""
            if path.stem in dup_counts:
                data.add_field(
                    "file",
                    fd,
                    filename=path.stem + f"({dup_counts[path.stem]})" + _add_suffix,
                )
                dup_counts[path.stem] += 1
            else:
                data.add_field("file", fd, filename=path.stem)
                dup_counts[path.stem] = 1
            file_args.append(data)

        for filename, stream in (req_kwargs.pop("streams", {}) or {}).items():
            # similar operation as above.
            files.append(stream)
            data = aiohttp.FormData()
            if filename in dup_counts:
                data.add_field(
                    "file",
                    stream,
                    filename=filename + f"({dup_counts[filename]})" + _add_suffix,
                )
                dup_counts[filename] += 1
            else:
                data.add_field("file", stream, filename=filename)
                dup_counts[filename] = 1
            file_args.append(data)

        yield file_args

        if files:
            [f.close() for f in files]

    @aioretry((aiohttp.ClientConnectionError, aiohttp.ServerDisconnectedError))
    async def _make_request(
        self,
        method: str,
        path: str,
        headers: dict = None,
        _refreshed=False,
        **request_kwargs,
    ):
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
                            method, path, headers, **request_kwargs, data=data
                        )
                        for data in file_args
                    )
                )
                return [resp for resp_set in resps for resp in resp_set]
            async with getattr(self.request_session, method)(
                f"{self.base_url}{path}",
                headers=headers,
                verify_ssl=self.config.verify_ssl,
                **request_kwargs,
            ) as response:

                # If auth expired refresh
                if response.status == 401 and not _refreshed:
                    await self.get_short_lived_access_token()
                    return await self._make_request(
                        method, path, headers, _refreshed=True, **request_kwargs
                    )
                elif response.status == 401 and _refreshed:
                    raise IndicoAuthenticationFailed()

                if response.status == 503 and "Retry-After" in response.headers:
                    raise IndicoHibernationError(
                        after=response.headers.get("Retry-After")
                    )

                if response.status >= 500:
                    raise IndicoRequestError(
                        code=response.status_code,
                        error=response.reason,
                        extras=repr(response.content),
                    )

                content = await aio_deserialize(
                    response, force_json=json, force_decompress=decompress
                )

                if response.status >= 400:
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
