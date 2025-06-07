"""yampyc: configuration management package.

This package provides classes for working with configuration:
- ``Yampyc`` – the main configuration class supporting multiple sources.
- ``YampycFactory`` – a factory for creating and managing configuration singletons.

Example usage:
    from yampyc import Yampyc, YampycFactory

    # Create configuration and load data from files
    config = Yampyc()
    config.add_yaml_source('config.yaml')
    config.add_env_source('.env')

    # Register configuration in the factory
    YampycFactory.set_config(config)

    # Retrieve configuration from the factory
    config = YampycFactory.get_config()
    print(config.get('some_key'))
"""

from yampyc._internal._yampyc import (
    Yampyc,
    YampycFactory,
    YampycNode,
)

__all__ = ['Yampyc', 'YampycFactory', 'YampycNode']
