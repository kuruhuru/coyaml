"""Injection of typed collections.

Run:
    PYTHONPATH=src uv run python examples/injection/26_inject_collections.py
"""

from __future__ import annotations

from typing import Annotated

from pydantic import BaseModel

from coyaml import YRegistry, YResource, YSettings, coyaml


class BModel(BaseModel):
    name: str


def setup() -> None:
    YRegistry.set_config(
        YSettings({'services': {'s1': {'name': 'a'}, 's2': {'name': 'b'}}, 'items': [{'name': 'a'}, {'name': 'b'}]})
    )


@coyaml
def handler_dict(svcs: Annotated[dict[str, BModel] | None, YResource('services')] = None) -> dict[str, BModel] | None:
    return svcs


@coyaml
def handler_list(items: Annotated[list[BModel] | None, YResource('items')] = None) -> list[BModel] | None:
    return items


def main() -> None:
    setup()
    print('dict:', {k: v.model_dump() for k, v in (handler_dict() or {}).items()})
    print('list:', [m.model_dump() for m in handler_list() or []])


if __name__ == '__main__':
    main()
