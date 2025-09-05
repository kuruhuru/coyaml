from __future__ import annotations

from typing import Annotated

import pytest

from coyaml import YRegistry, YResource, coyaml
from coyaml import YSettings as YConfig


def setup_config(data: dict[str, object]) -> None:
    cfg = YConfig(data)
    YRegistry.set_config(cfg)


def test_relative_path_positive_with_mask() -> None:
    setup_config({'env': {'services': {'a': 1}}, 'other': {'services': {'a': 2}}})

    @coyaml(mask='env.**')
    def func(svcs: Annotated[dict[str, int] | None, YResource('services')] = None) -> dict[str, int] | None:
        return svcs

    assert func() == {'a': 1}


def test_relative_path_ambiguous_raises() -> None:
    setup_config({'env': {'services': {'a': 1}}, 'other': {'services': {'a': 2}}})

    @coyaml
    def func(svcs: Annotated[dict[str, int] | None, YResource('services')] = None) -> dict[str, int] | None:  # noqa: ARG001
        return None

    with pytest.raises(KeyError, match="Ambiguous relative path suffix 'services'"):
        func()


def test_relative_path_optional_none() -> None:
    setup_config({'env': {'x': 1}})

    @coyaml
    def func(svcs: Annotated[dict[str, int] | None, YResource('services')] = None) -> dict[str, int] | None:
        return svcs

    assert func() is None


def test_absolute_path_prefix_caret() -> None:
    setup_config({'env': {'services': {'a': 1}}})

    @coyaml
    def func(svcs: Annotated[dict[str, int], YResource('^env.services')]) -> dict[str, int]:
        return svcs

    assert func() == {'a': 1}
