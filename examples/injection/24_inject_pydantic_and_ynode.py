"""Pydantic conversion and YNode passthrough in injection.

Run:
    PYTHONPATH=src uv run python examples/injection/24_inject_pydantic_and_ynode.py
"""

from __future__ import annotations

from typing import Annotated

from pydantic import BaseModel

from coyaml import YNode, YRegistry, YResource, YSettings, coyaml


class DB(BaseModel):
    user: str


def setup() -> None:
    YRegistry.set_config(YSettings({'debug': {'db': {'user': 'dev_user'}}}))


@coyaml(mask='debug.**')
def handler_pydantic(db: Annotated[DB | None, YResource()] = None) -> DB | None:
    # If annotation expects a Pydantic model, YNode is converted via .to()
    return db


@coyaml(mask='debug.**')
def handler_ynode(db: Annotated[YNode | None, YResource()] = None) -> YNode | None:
    # If annotation allows YNode, no conversion is performed
    return db


def main() -> None:
    setup()
    print('pydantic:', handler_pydantic())
    print('ynode:', handler_ynode())


if __name__ == '__main__':
    main()
