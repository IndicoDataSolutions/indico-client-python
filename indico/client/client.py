from indico.config import IndicoConfig
from indico.graphql.client import GraphClient
class IndicoClient:
    def __init___(self, config: IndicoConfig=None):
        if not config:
            config = IndicoConfig()
        self.config = config

        