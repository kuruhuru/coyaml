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

from coyaml._internal.config import YConfig
from coyaml._internal.deps import YDeps
from coyaml._internal.inject import ConfigKey, DepName, coyaml
from coyaml._internal.node import YNode
from coyaml._internal.registry import YRegistry
from coyaml.sources.base import YSource

__all__ = [
    'YConfig',
    'YNode',
    'YDeps',
    'YRegistry',
    'YSource',
    'coyaml',
    'ConfigKey',
    'DepName',
]
