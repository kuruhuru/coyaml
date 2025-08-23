"""Ambiguous matches and error diagnostics.

Run:
    PYTHONPATH=src uv run python examples/injection/25_inject_ambiguous_and_errors.py
"""

from __future__ import annotations

from typing import Annotated

from coyaml import YRegistry, YResource, YSettings, coyaml


def setup() -> None:
    YRegistry.set_config(YSettings({'a': {'user': 'x'}, 'b': {'user': 'y'}}))


@coyaml
def handler(user: Annotated[str | None, YResource()] = None) -> str | None:
    return user


def main() -> None:
    setup()
    try:
        handler()
    except KeyError as e:
        print('ambiguous error:', str(e))

    # Resolving ambiguity via mask
    from coyaml import coyaml as deco  # reuse decorator with mask

    @deco(mask='a.**')
    def handler_masked(user: Annotated[str | None, YResource()] = None) -> str | None:
        return user

    print('masked user =', handler_masked())


if __name__ == '__main__':
    main()
