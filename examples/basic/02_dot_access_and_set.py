"""Dot access vs dotted keys; setting values and nested creation.

Run:
    PYTHONPATH=src uv run python examples/basic/02_dot_access_and_set.py
"""

from __future__ import annotations

from coyaml import YNode, YSettings


def main() -> None:
    cfg = YSettings()

    # Assign flat values via attributes and dotted keys.
    cfg.index = 1
    cfg['llm'] = 'gpt'

    # Create nested structure with a dotted key; intermediate dicts are created automatically.
    cfg['debug.db.url'] = 'sqlite:///example.db'

    # Nested dictionaries are wrapped as YNode for convenient attribute access.
    assert isinstance(cfg.debug, YNode)  # noqa: S101
    assert cfg.debug.db.url == 'sqlite:///example.db'  # noqa: S101

    print('index =', cfg.index)
    print('llm =', cfg['llm'])
    print('db_url =', cfg.debug.db.url)


if __name__ == '__main__':
    main()
