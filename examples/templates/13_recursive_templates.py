"""Recursive templates resolution.

Run:
    PYTHONPATH=src uv run python examples/templates/13_recursive_templates.py
"""

from __future__ import annotations

import os

from coyaml import YSettings


def main() -> None:
    os.environ['A'] = '${{ env:B }}'
    os.environ['B'] = 'final'
    cfg = YSettings({'value': '${{ env:A }}'})
    cfg.resolve_templates()
    print('value =', cfg['value'])


if __name__ == '__main__':
    main()
