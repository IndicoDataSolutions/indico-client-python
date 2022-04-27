from typing import List
from indico.types.base import BaseType, JSONType
from datetime import datetime

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

def test_nested_empty_list_base_type():
    class A(BaseType):
        id: int

    class B(BaseType):
        id: int
        a: List[A]

    x = B(**{"id": 1, "a": []})
    assert x.id == 1
    assert x.a is not None
    assert len(x.a) == 0


def test_nested_list_simple_type():
    class B(BaseType):
        id: int
        a: List[str]

    x = B(**{"id": 1, "a": ["this is meta"]})
    assert x.id == 1
    assert x.a[0] == "this is meta"



def test_nested_empty_list_simple_type():

    class B(BaseType):
        id: int
        a: List[str]

    x = B(**{"id": 1, "a": []})
    assert x.id == 1
    assert x.a is not None


def test_camel_case_properties():
    class A(BaseType):
        something_in_snake: str

    x = A(**{"somethingInSnake": "sssss"})

    assert x.something_in_snake == "sssss"


def test_json_field():
    class A(BaseType):
        json_field: JSONType

    x = A(**{"jsonField": '{"test": "ing"}'})

    assert x.json_field == {"test": "ing"}


def test_timestamp_to_datetime_field():
    class A(BaseType):
        created_at: datetime

    x = A(**{"createdAt": '1590169591.582852'})

    assert x.created_at == datetime.fromtimestamp(1590169591.582852)
