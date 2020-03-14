import json
from typing import List
from indico.client.request import HTTPMethod, HTTPRequest


class RetrieveStorageObject(HTTPRequest):
    def __init__(self, storage_object):
        if type(storage_object) == dict:
            url = storage_object["url"]
        else:
            url = storage_object

        url = url.replace("indico-file://", "")
        super().__init__(method=HTTPMethod.GET, path=url)