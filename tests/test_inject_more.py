from __future__ import annotations

from typing import Annotated

import pytest

from coyaml import YRegistry, YResource, coyaml
from coyaml import YSettings as YConfig


def setup(data: dict[str, object]) -> None:
    YRegistry.set_config(YConfig(data))


def test_inject_not_found_non_optional_raises_keyerror() -> None:
    setup({'debug': {}})

    @coyaml(mask='debug.**')
    def handler(user: Annotated[str, YResource()]) -> str:
        return user

    with pytest.raises(KeyError, match="Key by name 'user' not found"):
        handler()


def test_inject_unique_false_returns_first_match() -> None:
    setup({'a': {'user': 'x'}, 'b': {'user': 'y'}})

    @coyaml(unique=False)
    def handler(user: Annotated[str, YResource()]) -> str:
        return user

    assert handler() == 'x'
