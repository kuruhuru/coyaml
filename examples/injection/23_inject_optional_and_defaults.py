"""Optional and default None behavior when value is not found.

Run:
    PYTHONPATH=src uv run python examples/injection/23_inject_optional_and_defaults.py
"""

from __future__ import annotations

from typing import Annotated

from coyaml import YRegistry, YResource, YSettings, coyaml


def setup() -> None:
    YRegistry.set_config(YSettings({'debug': {}}))


@coyaml
def handler_optional(token: Annotated[str | None, YResource()] = None) -> str | None:
    # Optional or default None prevents errors when value is not found
    return token


@coyaml
def handler_default(token: Annotated[str | None, YResource()] = None) -> str | None:
    return token


def main() -> None:
    setup()
    print('optional =', handler_optional())
    print('default  =', handler_default())


if __name__ == '__main__':
    main()
