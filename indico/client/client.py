# -*- coding: utf-8 -*-

from typing import Union
import urllib3

from indico.config import IndicoConfig
from indico.http.client import HTTPClient
from indico.client.request import HTTPRequest, RequestChain


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
