"""Quickstart: load YAML, resolve templates, and read values.

How to run locally:
    PYTHONPATH=src uv run python examples/basic/01_quickstart.py

This example intentionally uses the shared config file under examples/config.
"""

from __future__ import annotations

import os
from pathlib import Path

from coyaml import YSettings
from coyaml.sources.yaml import YamlFileSource


def main() -> None:
    # Set environment variables required by the example templates.
    # Note: never do this in production code; prefer a real environment or .env.
    os.environ['DB_USER'] = 'quick_user'
    os.environ['DB_PASSWORD'] = 'quick_password'  # noqa: S105

    # Initialize settings and load YAML from the examples folder.
    cfg = YSettings()
    cfg_path = Path(__file__).resolve().parents[1] / 'config' / 'config.yaml'
    cfg.add_source(YamlFileSource(cfg_path.as_posix()))

    # Resolve all templates (env, file, config, yaml) after loading.
    cfg.resolve_templates()

    # Read values using attribute access (dot notation) and dotted keys.
    print('index =', cfg.index)
    print('llm =', cfg['llm'])
    print('db_url =', cfg['debug.db.url'])
    print('db_user =', cfg.debug.db.user)


if __name__ == '__main__':
    main()
