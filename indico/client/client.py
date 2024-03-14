# -*- coding: utf-8 -*-

from typing import Union, Optional
import urllib3
import time
import asyncio
from indico.config import IndicoConfig
from indico.errors import IndicoError
from indico.http.client import HTTPClient, AIOHTTPClient
from indico.client.request import (
    HTTPRequest,
    RequestChain,
    PagedRequest,
    GraphQLRequest,
)


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

    def __init__(self, config: Optional[IndicoConfig] = None):
        if not config:
            config = IndicoConfig()
        if not config.verify_ssl:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        self.config = config
        self._http = HTTPClient(config)

    def _handle_request_chain(self, chain: RequestChain):
        response = None
        for request in chain.requests():
            print(request)
            if isinstance(request, HTTPRequest):
                response = self._http.execute_request(request)
                chain.previous = response
            elif isinstance(request, RequestChain):
                response = self._handle_request_chain(request)
                chain.previous = response
            elif isinstance(request, (float, int)):
                time.sleep(request)
        if chain.result:
            return chain.result
        return response

    def get_ipa_version(self):
        return self._http.execute_request(
            GraphQLRequest("query getIPAVersion {\n  ipaVersion\n}\n")
        )["ipaVersion"]

    def call(self, request: Union[HTTPRequest, RequestChain]):
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
        elif request and isinstance(request, HTTPRequest):
            return self._http.execute_request(request)

    def paginate(self, request: PagedRequest):
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

    def __init__(self, config: Optional[IndicoConfig] = None):
        if not config:
            config = IndicoConfig()
        if not config.verify_ssl:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        self.config = config
        self._http = AIOHTTPClient(config)
        self._created = False

    async def __aenter__(self):
        return await self.create()

    async def __aexit__(self, exc_type, exc, tb):
        await self.cleanup()

    async def create(self):
        await self._http.get_short_lived_access_token()
        self._created = True
        return self

    async def cleanup(self):
        await self._http.request_session.close()

    async def _handle_request_chain(self, chain: RequestChain):
        response = None
        for request in chain.requests():
            print(request)
            if isinstance(request, HTTPRequest):
                response = await self._http.execute_request(request)
                chain.previous = response
            elif isinstance(request, RequestChain):
                response = await self._handle_request_chain(request)
                chain.previous = response
            elif isinstance(request, (float, int)):
                asyncio.sleep(request)
        if chain.result:
            return chain.result
        return response

    async def get_ipa_version(self):
        if not self._created:
            raise IndicoError("Please .create() your client")
        return (
            await self._http.execute_request(
                GraphQLRequest("query getIPAVersion {ipaVersion}")
            )
        )["ipaVersion"]

    async def call(self, request: Union[HTTPRequest, RequestChain]):
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
        elif request and isinstance(request, HTTPRequest):
            return await self._http.execute_request(request)

    async def paginate(self, request: PagedRequest):
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
