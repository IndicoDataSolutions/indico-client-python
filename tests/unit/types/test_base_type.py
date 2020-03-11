from typing import List
from indico.types.base import BaseType

def test_setting_attributes_from_dict():
    class A(BaseType):
        id: int

    x = A(id=1)
    assert x.id == 1

def test_nested_base_type():
    class A(BaseType):
        id: int

    class B(BaseType):
        id: int
        a: A

    x = B(**{"id": 1, "a": {"id": 2}})
    assert x.id == 1
    assert x.a.id == 2


def test_nested_list_base_type():
    class A(BaseType):
        id: int

    class B(BaseType):
        id: int
        a: List[A]

    x = B(**{"id": 1, "a": [{"id": 2}]})
    assert x.id == 1
    assert x.a[0].id == 2
    

def test_nested_list_simple_type():

    class B(BaseType):
        id: int
        a: List[str]

    x = B(**{"id": 1, "a": ["this is meta"]})
    assert x.id == 1
    assert x.a[0] == "this is meta"