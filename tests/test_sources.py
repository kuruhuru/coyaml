from __future__ import annotations

from coyaml import YSettings
from coyaml.sources.env import EnvFileSource
from coyaml.sources.yaml import YamlFileSource


def test_sources_add_and_resolve() -> None:
    cfg = YSettings()
    cfg.add_source(YamlFileSource('tests/config/config.yaml'))
    cfg.add_source(EnvFileSource('tests/config/config.env'))
    cfg.resolve_templates()
    assert cfg['index'] == 9
    assert cfg['ENV1'] == '1.0'
