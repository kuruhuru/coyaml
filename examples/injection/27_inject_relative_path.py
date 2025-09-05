"""Relative path injection with masks.

Run:
    PYTHONPATH=src uv run python examples/injection/27_inject_relative_path.py
"""

from __future__ import annotations

from typing import Annotated

from coyaml import YRegistry, YResource, YSettings, coyaml


def setup() -> None:
    YRegistry.set_config(YSettings({'env': {'services': {'a': 1}}, 'other': {'services': {'a': 2}}, 'env2': {'x': 0}}))


@coyaml(mask='env.**')
def handler_relative(svcs: Annotated[dict[str, int] | None, YResource('services')] = None) -> dict[str, int] | None:
    return svcs


@coyaml
def handler_absolute(svcs: Annotated[dict[str, int], YResource('^env.services')]) -> dict[str, int]:
    return svcs


def main() -> None:
    setup()
    print('relative via mask:', handler_relative())
    print('absolute via ^   :', handler_absolute())


if __name__ == '__main__':
    main()
