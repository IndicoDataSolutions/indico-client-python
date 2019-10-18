from unittest.mock import patch

from indicoio.client import RequestProxy
from indicoio.api.base import ObjectProxy


@patch.object(RequestProxy, "_make_request")
def test_object_proxy_in(mock_request_proxy):
    obj_proxy = ObjectProxy(mock_arg="mock_arg_value")
    assert "mock_arg" in obj_proxy, obj_proxy


@patch.object(RequestProxy, "_make_request")
def test_object_proxy_attrs(mock_request_proxy):
    obj_proxy = ObjectProxy(mock_arg="mock_arg_value")
    assert obj_proxy["mock_arg"] == "mock_arg_value"
    obj_proxy["mock_arg"] = "mock_arg_value_new"
    assert obj_proxy["mock_arg"] == "mock_arg_value_new", "Did not update to new value"


@patch.object(RequestProxy, "_make_request")
def test_object_proxy_build(mock_request_proxy):
    obj_proxy = ObjectProxy(mock_arg="mock_arg_value")

    new_obj = obj_proxy.build_object(ObjectProxy, new_arg="new_arg")
    assert isinstance(new_obj, ObjectProxy)
    assert new_obj["new_arg"] == "new_arg"


@patch.object(RequestProxy, "_make_request")
def test_object_proxy_get(mock_request_proxy):
    obj_proxy = ObjectProxy(mock_arg="mock_arg_value")

    assert obj_proxy.get("mock_arg") == "mock_arg_value"
    assert obj_proxy.get("mock_argx") is None
    assert obj_proxy.get("mock_argx", False) is False

