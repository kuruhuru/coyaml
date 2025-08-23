from __future__ import annotations

import pytest

from coyaml import YRegistry
from coyaml.sources.yaml import YamlFileSource


def test_registry_set_get_remove() -> None:
    from coyaml import YSettings

    cfg = YSettings({'x': 1})
    YRegistry.set_config(cfg, 'k')
    assert YRegistry.get_config('k')['x'] == 1
    YRegistry.remove_config('k')
    with pytest.raises(KeyError):
        YRegistry.get_config('k')


def test_registry_uri_helpers_with_registered_scheme() -> None:
    # register a simple yaml scheme
    YRegistry.register_scheme('yaml', YamlFileSource)

    # create from a single uri
    cfg = YRegistry.create_from_uri('yaml://tests/config/config.yaml')
    # last source wins in create_from_uri_list; here it's a single yaml
    assert cfg['index'] == 9
