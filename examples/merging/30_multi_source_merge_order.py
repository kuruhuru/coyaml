"""Merging multiple sources: later sources override earlier ones; dicts are deep-merged.

Run:
    PYTHONPATH=src uv run python examples/merging/30_multi_source_merge_order.py
"""

from __future__ import annotations

from coyaml import YSettings
from coyaml.sources.yaml import YamlFileSource


def main() -> None:
    cfg = YSettings()
    # Base config
    cfg.add_source(YamlFileSource('tests/config/config.yaml'))
    # Overlay with changes
    cfg.add_source(
        YamlFileSource('tests/config/extra.yaml')
    )  # this is a different shape; used here only to show precedence

    # Resolve templates after all sources are added
    cfg.resolve_templates()

    print('llm =', cfg['llm'])
    print('debug.db.user =', cfg['debug.db.user'])


if __name__ == '__main__':
    main()
