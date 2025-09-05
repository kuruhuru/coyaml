from __future__ import annotations

from typing import Annotated

from pydantic import BaseModel

from coyaml import YRegistry, YResource, coyaml
from coyaml import YSettings as YConfig


class BModel(BaseModel):
    name: str


def setup_config(data: dict[str, object]) -> None:
    cfg = YConfig(data)
    YRegistry.set_config(cfg)


def test_inject_dict_of_model() -> None:
    setup_config({'services': {'s1': {'name': 'a'}, 's2': {'name': 'b'}}})

    @coyaml
    def func(svcs: Annotated[dict[str, BModel] | None, YResource('services')] = None) -> dict[str, BModel] | None:
        return svcs

    result = func()
    assert result is not None
    assert set(result.keys()) == {'s1', 's2'}
    assert all(isinstance(v, BModel) for v in result.values())


def test_inject_list_of_model() -> None:
    setup_config({'services': [{'name': 'a'}, {'name': 'b'}]})

    @coyaml
    def func(items: Annotated[list[BModel] | None, YResource('services')] = None) -> list[BModel] | None:
        return items

    result = func()
    assert result is not None
    assert [m.name for m in result] == ['a', 'b']
