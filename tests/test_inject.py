from __future__ import annotations

from typing import Annotated

import pytest
from pydantic import BaseModel

from coyaml import YNode, YRegistry, YResource, coyaml
from coyaml import YSettings as YConfig


def setup_config(data: dict[str, object]) -> None:
    cfg = YConfig(data)
    YRegistry.set_config(cfg)


def test_inject_lookup_by_name_no_mask_unique() -> None:
    setup_config({'user': 'u', 'nested': {'x': 1}})

    @coyaml
    def func(user: Annotated[str | None, YResource()] = None) -> str | None:
        return user

    assert func() == 'u'


def test_inject_lookup_by_name_with_mask() -> None:
    setup_config({'debug': {'db': {'user': 'du'}}, 'prod': {'db': {'user': 'pu'}}})

    @coyaml(mask='debug.**')
    def func(user: Annotated[str | None, YResource()] = None) -> str | None:
        return user

    assert func() == 'du'


def test_inject_ambiguous_raises() -> None:
    setup_config({'a': {'user': 'x'}, 'b': {'user': 'y'}})

    @coyaml
    def func(user: Annotated[str | None, YResource()] = None) -> str | None:  # noqa: ARG001
        return None

    with pytest.raises(KeyError, match="Ambiguous key name 'user'"):
        func()


def test_inject_optional_none_when_not_found() -> None:
    setup_config({'debug': {'db': {'user': 'du'}}})

    @coyaml
    def func(token: Annotated[str | None, YResource()] = None) -> str | None:
        return token

    assert func() is None


def test_inject_explicit_path() -> None:
    setup_config({'debug': {'db': {'user': 'du'}}})

    @coyaml
    def func(user: Annotated[str, YResource('debug.db.user')]) -> str:
        return user

    assert func() == 'du'


def test_inject_list_with_mask() -> None:
    setup_config({'services': [{'user': 'a'}, {'user': 'b'}]})

    @coyaml(mask='services.*.**', unique=False)
    def func(user: Annotated[str | None, YResource()] = None) -> str | None:
        return user

    assert func() == 'a'


class DB(BaseModel):
    user: str


def test_inject_pydantic_conversion_via_search() -> None:
    setup_config({'debug': {'db': {'user': 'du'}}})

    @coyaml(mask='debug.**')
    def func(db: Annotated[DB | None, YResource()] = None) -> DB | None:
        return db

    result = func()
    assert isinstance(result, DB)
    assert result.user == 'du'


def test_inject_ynode_passthrough_via_search() -> None:
    setup_config({'debug': {'db': {'user': 'du'}}})

    @coyaml(mask='debug.**')
    def func(db: Annotated[YNode | None, YResource()] = None) -> YNode | None:
        return db

    result = func()
    assert isinstance(result, YNode)
    assert result['user'] == 'du'
