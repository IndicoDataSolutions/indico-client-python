from typing import Union, Dict, Any

from indico.config import IndicoConfig
from indico.http.client import HTTPClient
from indico.client.request import GraphQLRequest, HTTPRequest, RequestChain

class IndicoClient:
    
    def __init__(self, config: IndicoConfig=None):
        if not config:
            config = IndicoConfig()
        self.config = config
        self._http = HTTPClient(config)

    def _handle_request_chain(self, chain: RequestChain):
        response = None
        for request in chain.requests():
            response = self._http.execute_request(request)
            chain.previous = response

        return response

    def call(self, request: Union[HTTPRequest, RequestChain]):
        """
        Make a call to the indico IPA platform
        """
        if isinstance(request, RequestChain):
            return self._handle_request_chain(request)
        elif request and isinstance(request, HTTPRequest):
            return self._http.execute_request(request)
