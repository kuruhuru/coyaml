"""Injection by parameter name constrained by mask.

Run:
    PYTHONPATH=src uv run python examples/injection/22_inject_by_name_with_mask.py
"""

from __future__ import annotations

from typing import Annotated

from coyaml import YRegistry, YResource, YSettings, coyaml


def setup() -> None:
    cfg = YSettings({'debug': {'db': {'user': 'dev_user'}}, 'prod': {'db': {'user': 'prod_user'}}})
    YRegistry.set_config(cfg)


@coyaml(mask='debug.**')
def handler(user: Annotated[str | None, YResource()] = None) -> str | None:
    return user


def main() -> None:
    setup()
    print('user =', handler())


if __name__ == '__main__':
    main()
