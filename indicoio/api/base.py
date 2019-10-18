from indicoio.client import RequestProxy
from indicoio.graphql import GraphClient
from indicoio.config import RequestConfigMixin


class ObjectProxy(RequestConfigMixin):
    def __init__(self, config_options=None, **object_attrs):
        super().__init__(config_options)
        self.graphql = GraphClient(config_options=self.config_options)
        self.object_attrs = object_attrs or {}

    def get(self, *args, **kwargs):
        return self.object_attrs.get(*args, **kwargs)

    def __getitem__(self, *args, **kwargs):
        return self.object_attrs.__getitem__(*args, **kwargs)

    def __setitem__(self, *args, **kwargs):
        self.object_attrs.__setitem__(*args, **kwargs)

    def __iter__(self):
        return self.object_attrs.__iter__()

    def update(self, dict_obj):
        self.object_attrs.update(dict_obj)

    def build_object(self, object_cls, **values):
        return object_cls(config_options=self.config_options, **values)
