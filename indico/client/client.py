# -*- coding: utf-8 -*-

import asyncio
import time
from typing import TYPE_CHECKING, cast

import urllib3

from indico.client.request import Delay, HTTPRequest, RequestChain
from indico.config import IndicoConfig
from indico.errors import IndicoError
from indico.http.client import AIOHTTPClient, HTTPClient
from indico.queries.version import GetIPAVersion

if TYPE_CHECKING:  # pragma: no cover
    from types import TracebackType
    from typing import Any, AsyncIterator, Iterator, Optional, Type, TypeVar, Union

    from typing_extensions import Self

    from indico.client.request import PagedRequest

    ReturnType = TypeVar("ReturnType")


class IndicoClient:
    """
    The Indico GraphQL Client.

    IndicoClient is the primary way to interact with the Indico Platform.

    Args:
        config= (IndicoConfig, optional): IndicoConfig object with environment configuration

    Returns:
        IndicoConfig object

    Raises:
        RuntimeError: If api_token_path does not exist.
    """

    def __init__(self, config: "Optional[IndicoConfig]" = None):
        if not config:
            config = IndicoConfig()

        if not config.verify_ssl:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        self.config = config
        self._http = HTTPClient(config)

    def _handle_request_chain(
        self,
        chain: "RequestChain[Any, ReturnType]",
    ) -> "ReturnType":
        response: "Optional[ReturnType]" = None

        for request in chain.requests():
            if isinstance(request, RequestChain):
                response = self._handle_request_chain(request)
                chain.previous = response
            elif isinstance(request, HTTPRequest):
                response = self._http.execute_request(request)
                chain.previous = response
            elif isinstance(request, Delay):
                time.sleep(request.seconds)

        if chain.result is not None:
            return chain.result

        return cast("ReturnType", response)

    def get_ipa_version(self) -> str:
        return self.call(GetIPAVersion())

    def call(
        self,
        request: "Union[HTTPRequest[Any, ReturnType], RequestChain[Any, ReturnType]]",
    ) -> "ReturnType":
        """
        Make a call to the Indico IPA Platform

        Args:
            request (GraphQLRequest or RequestChain): GraphQL request to send to the Indico Platform

        Returns:
            Response appropriate to the class of the provided request parameter. Often JSON, but not always.

        Raises:
            IndicoRequestError: With errors in processing the request
        """

        if isinstance(request, RequestChain):
            return self._handle_request_chain(request)
        elif isinstance(request, HTTPRequest):
            return self._http.execute_request(request)
        else:
            raise ValueError(
                "Invalid request type! Must be one of HTTPRequest or RequestChain."
            )

    def paginate(self, request: "PagedRequest[ReturnType]") -> "Iterator[ReturnType]":
        """
        Provides a generator that continues paging through responses
        Available with List<> Requests that offer pagination

        Example:
            for s in client.paginate(ListSubmissions()):
                print("Submission", s)
        """
        while request.has_next_page:
            r = self._http.execute_request(request)
            yield r


class AsyncIndicoClient:
    """
    The Async Indico GraphQL Client.
    Notably, this client does not offer the usage of
    `_disable_cookie_domain`

    You must explicitly create and close this client
        client = await AsyncIndicoClient(config=config).create()
        # ... do stuff
        await client.cleanup()

    or implicitly using a `with` statement
        async with AsyncIndicoClient(config=config) as client:
            # ... do stuff

    Args:
        config= (IndicoConfig, optional): IndicoConfig object with environment configuration

    Returns:
        IndicoConfig object

    Raises:
        RuntimeError: If api_token_path does not exist.
    """

    def __init__(self, config: "Optional[IndicoConfig]" = None):
        if not config:
            config = IndicoConfig()
        if not config.verify_ssl:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        self.config = config
        self._http = AIOHTTPClient(config)
        self._created: bool = False

    async def __aenter__(self) -> "Self":
        return await self.create()

    async def __aexit__(
        self,
        exc_type: "Optional[Type[BaseException]]",
        exc: "Optional[BaseException]",
        tb: "Optional[TracebackType]",
    ) -> None:
        await self.cleanup()

    async def create(self) -> "Self":
        await self._http.get_short_lived_access_token()
        self._created = True
        return self

    async def cleanup(self) -> None:
        await self._http.request_session.close()

    async def _handle_request_chain(
        self,
        chain: "RequestChain[Any, ReturnType]",
    ) -> "ReturnType":
        response: "Optional[ReturnType]" = None

        for request in chain.requests():
            if isinstance(request, RequestChain):
                response = await self._handle_request_chain(request)
                chain.previous = response
            elif isinstance(request, HTTPRequest):
                response = await self._http.execute_request(request)
                chain.previous = response
            elif isinstance(request, Delay):
                await asyncio.sleep(request.seconds)

        if chain.result is not None:
            return chain.result

        return cast("ReturnType", response)

    async def get_ipa_version(self) -> str:
        return await self.call(GetIPAVersion())

    async def call(
        self,
        request: "Union[HTTPRequest[Any, ReturnType], RequestChain[Any, ReturnType]]",
    ) -> "ReturnType":
        """
        Make a call to the Indico IPA Platform

        Args:
            request (GraphQLRequest or RequestChain): GraphQL request to send to the Indico Platform

        Returns:
            Response appropriate to the class of the provided request parameter. Often JSON but not always.

        Raises:
            IndicoRequestError: With errors in processing the request
        """
        if not self._created:
            raise IndicoError("Please .create() your client")

        if isinstance(request, RequestChain):
            return await self._handle_request_chain(request)
        elif isinstance(request, HTTPRequest):
            return await self._http.execute_request(request)
        else:
            raise ValueError(
                "Invalid request type! Must be one of HTTPRequest or RequestChain."
            )

    async def paginate(
        self, request: "PagedRequest[ReturnType]"
    ) -> "AsyncIterator[ReturnType]":
        """
        Provides a generator that continues paging through responses
        Available with List<> Requests that offer pagination

        Example:
            async for s in client.paginate(ListSubmissions()):
                print("Submission", s)
        """
        if not self._created:
            raise IndicoError("Please .create() your client")
        while request.has_next_page:
            r = await self._http.execute_request(request)
            yield r
