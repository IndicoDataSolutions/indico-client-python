from indicoio.client import RequestProxy


class ObjectProxy(object):
    def __init__(self, config_options=None, **object_attrs):
        self.object_attrs = object_attrs or {}
        self.request_client = RequestProxy(config_options)
