"""
Will be used for auto query template generation via introspection in the future.
Auto generation will occur on package build and push to correspond with indico graphql server versions
"""


class Query(object):
    def __init__(self, *fields, **queries):
        self.fields = fields
        self.queries = queries
        self._params = {}

    def params(self, **params_kwargs):
        self._params.update(params_kwargs)


"""
Query(user=Query("id", "api_refresh_token").params(id=812))
"""
