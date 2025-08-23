"""Injection by parameter name without mask (searches the whole tree).

Run:
    PYTHONPATH=src uv run python examples/injection/21_inject_by_name_no_mask.py
"""

from __future__ import annotations

from typing import Annotated

from coyaml import YRegistry, YResource, YSettings, coyaml


def setup() -> None:
    cfg = YSettings({'service': {'user': 'alice'}, 'user': 'bob'})
    YRegistry.set_config(cfg)


@coyaml
def handler(user: Annotated[str, YResource()]) -> str:
    # With duplicates in the tree this will raise an ambiguity error unless unique=False is used.
    return user


def main() -> None:
    setup()
    try:
        print('user =', handler())
    except KeyError as e:
        print('expected ambiguity:', str(e))


if __name__ == '__main__':
    main()
