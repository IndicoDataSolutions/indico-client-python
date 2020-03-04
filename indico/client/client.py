from typing import Union, Dict, Any

from indico.config import IndicoConfig
from indico.graphql.client import GraphQLClient
from indico.http.client import HttpClient
from indico.queries.query import BaseQuery
from indico.client.request import GraphQLRequest

class IndicoClient:
    def __init___(self, config: IndicoConfig=None):
        if not config:
            config = IndicoConfig()
        self.config = config

        self.http = HttpClient(config)
        self.graphql = GraphQLClient(config, self.http)

    def call(self, query: Union[str, BaseQuery], variables: Dict[str, Any]=None):
        if isinstance(query, str):
            return query.build_result(self.graphql.execute(GraphQLRequest(query=query, variables=variables)))        
        
        

        return query.build_result(self.graphql.execute(query, variables))