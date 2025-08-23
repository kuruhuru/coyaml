from __future__ import annotations

import os

from coyaml import YSettings
from coyaml.sources.env import EnvFileSource
from coyaml.sources.yaml import YamlFileSource


def test_sources_add_and_resolve() -> None:
    os.environ['DB_USER'] = 'test_user'
    cfg = YSettings()
    cfg.add_source(YamlFileSource('tests/config/config.yaml'))
    cfg.add_source(EnvFileSource('tests/config/config.env'))
    cfg.resolve_templates()
    assert cfg['index'] == 9
    assert cfg['ENV1'] == '1.0'
