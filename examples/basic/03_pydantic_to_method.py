"""Converting configuration (or subtrees) to Pydantic models using .to().

Run:
    PYTHONPATH=src uv run python examples/basic/03_pydantic_to_method.py
"""

from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel

from coyaml import YSettings
from coyaml.sources.yaml import YamlFileSource


class DatabaseConfig(BaseModel):
    url: str


class DebugConfig(BaseModel):
    db: DatabaseConfig


def main() -> None:
    cfg = YSettings()
    cfg_path = Path(__file__).resolve().parents[1] / 'config' / 'config.yaml'
    cfg.add_source(YamlFileSource(cfg_path.as_posix()))

    # Convert a subtree to a Pydantic model
    debug: DebugConfig = cfg.debug.to(DebugConfig)
    print('debug.db.url =', debug.db.url)

    # Convert the whole tree to a Pydantic model
    full: DebugConfig = cfg.to(DebugConfig)
    # Note: this will fail unless the top-level shape matches DebugConfig.
    # It is here to demonstrate that .to() can be called at any level.
    _ = full


if __name__ == '__main__':
    main()
