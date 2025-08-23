"""Limits of config/yaml templates inside strings.

Run:
    PYTHONPATH=src uv run python examples/templates/14_config_template_limits.py
"""

from __future__ import annotations

from coyaml import YSettings


def main() -> None:
    # config returning dict/list inside a string triggers ValueError
    cfg = YSettings({'dict': {'k': 'v'}, 'txt': 'prefix ${{ config:dict }} suffix'})
    try:
        cfg.resolve_templates()
    except ValueError as e:
        print('expected error (config in string):', str(e))

    # yaml inside a string is not allowed as well
    cfg = YSettings({'txt': 'prefix ${{ yaml:tests/config/extra.yaml }} suffix'})
    try:
        cfg.resolve_templates()
    except ValueError as e:
        print('expected error (yaml in string):', str(e))


if __name__ == '__main__':
    main()
