"""Injection by explicit dotted path using Annotated + YResource.

Run:
    PYTHONPATH=src uv run python examples/injection/20_inject_by_explicit_path.py
"""

from __future__ import annotations

from typing import Annotated

from coyaml import YRegistry, YResource, YSettings, coyaml
from coyaml.sources.yaml import YamlFileSource


def setup() -> None:
    cfg = YSettings()
    cfg.add_source(YamlFileSource('tests/config/config.yaml'))
    cfg.resolve_templates()
    YRegistry.set_config(cfg)


@coyaml
def handler(user: Annotated[str, YResource('debug.db.user')]) -> str:
    return user


def main() -> None:
    setup()
    print('user =', handler())


if __name__ == '__main__':
    main()
