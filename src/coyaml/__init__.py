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

from coyaml._internal._config import (
    YConfig,
    YConfigFactory,
    YNode,
)

__all__ = ['YConfig', 'YConfigFactory', 'YNode']
