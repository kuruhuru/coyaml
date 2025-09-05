"""
coyaml: Package for managing YAML configuration

This package provides classes for working with configurations:
- YConfig: Class for working with configuration, supporting various data sources.
- YConfigFactory: Factory for creating and managing configuration singletons using optional keys.

Usage example:
    from coyaml import YConfig, YConfigFactory

    # Create configuration and load data from files
    config = YConfig()
    config.add_yaml_source('config.yaml')
    config.add_env_source('.env')

    # Set configuration in factory
    YConfigFactory.set_config(config)

    # Get configuration from factory
    config = YConfigFactory.get_config()
    print(config.get('some_key'))
"""

# Legacy imports for backward compatibility
from coyaml._internal import inject as _inject
from coyaml._internal._config import YConfig, YConfigFactory
from coyaml._internal.config import YSettings
from coyaml._internal.inject import YResource
from coyaml._internal.node import YNode
from coyaml._internal.registry import YRegistry
from coyaml.sources.base import YSource
from coyaml.sources.env import EnvFileSource
from coyaml.sources.yaml import YamlFileSource
from coyaml.utils.merge import deep_merge

__all__ = [
    'YSettings',
    'YNode',
    'YRegistry',
    'YSource',
    'YamlFileSource',
    'EnvFileSource',
    'deep_merge',
    'YConfig',  # Legacy
    'YConfigFactory',  # Legacy
    'coyaml',
    'YResource',
]


def coyaml(_func=None, *, mask: str | list[str] | None = None, unique: bool = True):  # type: ignore
    """Public shim for the internal decorator to make docs and typing happy."""
    return _inject.coyaml(_func, mask=mask, unique=unique)
