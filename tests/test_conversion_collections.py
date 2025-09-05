from __future__ import annotations

from pydantic import BaseModel

from coyaml import YNode


class BModel(BaseModel):
    name: str
    enabled: bool | None = None


def test_to_dict_of_model() -> None:
    node = YNode({'key': {'first': {'name': 'svc', 'enabled': True}}})
    converted = node['key'].to(dict[str, BModel])
    assert isinstance(converted, dict)
    assert isinstance(converted['first'], BModel)
    assert converted['first'].name == 'svc'
    assert converted['first'].enabled is True


def test_to_dict_of_bool() -> None:
    node = YNode({'flags': {'x': 1, 'y': 'yes', 'z': False}})
    converted = node['flags'].to(dict[str, bool])
    assert converted == {'x': True, 'y': True, 'z': False}


def test_to_list_of_model() -> None:
    node = YNode({'items': [{'name': 'a'}, {'name': 'b', 'enabled': False}]})
    items = node['items']
    converted = items.to(list[BModel])
    assert isinstance(converted, list)
    assert [m.name for m in converted] == ['a', 'b']
    assert converted[1].enabled is False
