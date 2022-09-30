# -*- coding: utf-8 -*-
import concurrent.futures
from typing import Union

from indico.client.request import (
    GraphQLRequest,
    HTTPRequest,
    PagedRequest,
    RequestChain,
)
from indico.config import IndicoConfig
from indico.http.client import HTTPClient

import urllib3

THREAD_POOL = concurrent.futures.ThreadPoolExecutor(max_workers=8)


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

    def __init__(self, config: IndicoConfig = None):
        if not config:
            config = IndicoConfig()
        if not config.verify_ssl:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        self.config = config
        self._http = HTTPClient(config)

    def _handle_request_chain(self, chain: RequestChain):
        response = None
        for request in chain.requests():
            if isinstance(request, HTTPRequest):
                response = self._http.execute_request(request)
                chain.previous = response
            elif isinstance(request, RequestChain):
                response = self._handle_request_chain(request)
                chain.previous = response

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
            Response appropriate to the class of the provided request parameter. Often JSON but not always.

        Raises:
            IndicoRequestError: With errors in processing the request
        """

        if isinstance(request, RequestChain):
            return self._handle_request_chain(request)
        elif request and isinstance(request, HTTPRequest):
            return self._http.execute_request(request)

    def call_concurrent(self, requests: list[HTTPRequest]) -> list[dict]:
        """
        Make batched calls to Indico IPA Platform with thread pool.

        Args:
            request (GraphQLRequest or RequestChain): GraphQL request to send to the Indico Platform

        Returns:
            Response appropriate to the class of the provided request parameter. Often JSON but not always.

        Raises:
            IndicoRequestError: With errors in processing the request
        """
        data: list[dict] = []
        with THREAD_POOL as executor:
            for res in executor.map(self.call, requests):
                data.append(res)

        return data

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
