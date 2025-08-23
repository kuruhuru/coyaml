"""Templates showcase: env, file, config, yaml.

Run:
    PYTHONPATH=src uv run python examples/templates/10_env_file_config_yaml.py

This uses shared YAML under examples/config/config.yaml which contains all template types.
"""

from __future__ import annotations

import os
from pathlib import Path

from coyaml import YSettings
from coyaml.sources.yaml import YamlFileSource


def main() -> None:
    # Prepare environment for env templates
    os.environ['DB_USER'] = 'templ_user'
    os.environ['DB_PASSWORD'] = 'templ_password'  # noqa: S105

    cfg = YSettings()
    cfg_path = Path(__file__).resolve().parents[1] / 'config' / 'config.yaml'
    cfg.add_source(YamlFileSource(cfg_path.as_posix()))
    cfg.resolve_templates()

    # env
    print('env user:', cfg['debug.db.user'])
    # file (reads tests/config/init.sql)
    print('file snippet length:', len(cfg['debug.db.init_script']))
    # config (builds db_url from other values)
    print('config db_url:', cfg['app.db_url'])
    # yaml (loads and merges external yaml)
    print('yaml feature:', cfg['app.extra_settings.feature_flags.enable_new_feature'])


if __name__ == '__main__':
    main()
