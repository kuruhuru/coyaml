"""
yampyc: Package for managing YAMPYC configuration

This package provides classes for working with configurations:
- Yampyc: Class for working with configuration, supporting various data sources.
- YampycFactory: Factory for creating and managing configuration singletons using optional keys.

Usage example:
    from yampyc import Yampyc, YampycFactory

    # Create configuration and load data from files
    config = Yampyc()
    config.add_yaml_source('config.yaml')
    config.add_env_source('.env')

    # Set configuration in factory
    YampycFactory.set_config(config)

    # Get configuration from factory
    config = YampycFactory.get_config()
    print(config.get('some_key'))
"""

from yampyc._internal._yampyc import (
    Yampyc,
    YampycFactory,
    YampycNode,
)

__all__ = ['Yampyc', 'YampycFactory', 'YampycNode']
