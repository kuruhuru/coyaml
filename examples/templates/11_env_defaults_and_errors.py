"""Environment template defaults and error handling.

Run:
    PYTHONPATH=src uv run python examples/templates/11_env_defaults_and_errors.py
"""

from __future__ import annotations

import os

from coyaml import YSettings


def main() -> None:
    cfg = YSettings({'db': {'user': '${{ env:DB_USER }}', 'password': '${{ env:DB_PASSWORD:secret }}'}})

    # Ensure DB_USER is not present to trigger ValueError
    os.environ.pop('DB_USER', None)

    try:
        cfg.resolve_templates()
    except ValueError as e:
        print('expected error:', str(e))

    # With DB_USER present resolution succeeds, and DB_PASSWORD falls back to default "secret"
    os.environ['DB_USER'] = 'ok'
    cfg = YSettings({'db': {'user': '${{ env:DB_USER }}', 'password': '${{ env:DB_PASSWORD:secret }}'}})
    cfg.resolve_templates()
    print('user:', cfg['db.user'])
    print('password:', cfg['db.password'])


if __name__ == '__main__':
    main()
