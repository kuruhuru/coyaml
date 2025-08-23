"""File and YAML includes with decoding rules.

Run:
    PYTHONPATH=src uv run python examples/templates/12_file_and_yaml_includes.py
"""

from __future__ import annotations

from pathlib import Path

from coyaml import YSettings


def main() -> None:
    base = Path('tests/config')
    cfg = YSettings(
        {
            'from_file': f'${{ file:{(base / "init.sql").as_posix()} }}',
            'from_yaml': f'${{ yaml:{(base / "extra.yaml").as_posix()} }}',
        }
    )
    cfg.resolve_templates()
    print('file length:', len(cfg['from_file']))
    print('yaml flag:', cfg['from_yaml.feature_flags.enable_new_feature'])


if __name__ == '__main__':
    main()
