from typing import Union, Dict, Any

from indico.config import IndicoConfig
from indico.http.client import HTTPClient, HTTPRequest
from indico.queries.query import BaseQuery
from indico.client.request import GraphQLRequest

class IndicoClient:
    
    def __init__(self, config: IndicoConfig=None):
        if not config:
            config = IndicoConfig()
        self.config = config
        self._http = HTTPClient(config)

    def _call_graphql_query(self, query: Union[str, BaseQuery], variables: Dict[str, Any]=None):
        if isinstance(query, str):
            query = GraphQLRequest(query=query, variables=variables)
        return query.process_response(self._http.execute_request(query))

    def call(self, request: Union[HTTPRequest, BaseQuery, str]=None, variables: Dict[str, Any]=None):
        """
        Make a call to the indico IPA platform
        """
        if isinstance(request, str) or isinstance(request, BaseQuery):
            return self._call_graphql_query(query=request, variables=variables)
        elif request and isinstance(request, HTTPRequest):
            return self._http.execute_request(request)
