"""
yampyc: Пакет для управления конфигурацией YAMPYC

Этот пакет предоставляет классы для работы с конфигурациями:
- Yampyc: Класс для работы с конфигурацией, поддерживающий различные источники данных.
- YampycFactory: Фабрика для создания и управления синглтонами конфигурации с использованием опциональных ключей.

Пример использования:
    from yampyc import Yampyc, YampycFactory

    # Создание конфигурации и загрузка данных из файлов
    config = Yampyc()
    config.add_yaml_source('config.yaml')
    config.add_env_source('.env')

    # Установка конфигурации в фабрику
    YampycFactory.set_config(config)

    # Получение конфигурации из фабрики
    config = YampycFactory.get_config()
    print(config.get('some_key'))
"""

from yampyc._internal._yampyc import (
    Yampyc,
    YampycFactory,
    YampycNode,
)

__all__ = ['Yampyc', 'YampycFactory', 'YampycNode']
