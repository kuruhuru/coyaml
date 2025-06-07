# src/yampyc/_internal/_yampyc.py
import importlib
import os
import re
from collections.abc import Iterator
from typing import (
    Any,
    TypeVar,
)

import yaml
from dotenv import load_dotenv
from pydantic import BaseModel

# Паттерн для поиска имен переменных
TEMPLATE_PATTERN = re.compile(r'\${{\s*(\w+):(.+?)}}')


# Определяем типовую переменную
T = TypeVar('T', bound='BaseModel')


class YampycNode:
    """
    Класс, представляющий узел конфигурации.
    Позволяет обращаться к вложенным параметрам конфигурации через атрибуты и ключи.
    """

    def __init__(self, data: dict[str, Any]):
        """
        Инициализация узла конфигурации.

        :param data: Словарь с данными конфигурации.
        """
        self._data = data

    def to_dict(self) -> dict[str, Any]:
        """
        Конвертирует узел конфигурации в словарь.
        """
        return self._data

    def __iter__(self) -> Iterator[str]:
        """
        Позволяет итерироваться по ключам конфигурации.
        """
        return iter(self._data)

    def items(self) -> Iterator[tuple[str, Any]]:
        """
        Позволяет итерироваться по ключам и значениям конфигурации, как в словаре.
        """
        return self._data.items()  # type: ignore

    def values(self) -> Any:
        """
        Позволяет итерироваться по значениям конфигурации.
        """
        return self._data.values()

    def __getattr__(self, item: str) -> Any:
        """
        Позволяет обращаться к параметрам конфигурации через атрибуты.

        :param item: Имя параметра.
        :return: Значение параметра или новый узел конфигурации, если параметр является словарем.
        :raises AttributeError: Если параметр не найден.
        """
        if item not in self._data:
            raise AttributeError(f"'YampycNode' object has no attribute '{item}'")
        value = self._data[item]
        if isinstance(value, dict):
            return YampycNode(value)
        elif isinstance(value, list):
            return [YampycNode(v) if isinstance(v, dict) else v for v in value]
        return value

    def __getitem__(self, item: str) -> Any:
        """
        Позволяет обращаться к параметрам конфигурации через ключи, используя точечную нотацию.

        :param item: Имя параметра или цепочка параметров через точку.
        :return: Значение параметра.
        :raises KeyError: Если параметр не найден.
        """
        keys = item.split('.')
        value = self._data

        for key in keys:
            if not isinstance(value, dict) or key not in value:
                raise KeyError(f"Key '{key}' not found in the configuration")
            value = value[key]

        if isinstance(value, dict):
            return YampycNode(value)
        elif isinstance(value, list):
            return [YampycNode(v) if isinstance(v, dict) else v for v in value]
        return value

    def __setattr__(self, key: str, value: Any) -> None:
        """
        Устанавливает значение параметра конфигурации через атрибуты.

        :param key: Имя параметра.
        :param value: Значение параметра.
        """
        if key == '_data':  # Исключение для внутреннего атрибута
            super().__setattr__(key, value)
        else:
            self._data[key] = self._convert_value(value)

    def __setitem__(self, key: str, value: Any) -> None:
        """
        Устанавливает значение параметра конфигурации через ключи.
        Поддерживается установка параметров с точечной нотацией.

        :param key: Имя параметра или цепочка параметров через точку.
        :param value: Значение параметра.
        """
        keys = key.split('.')
        d = self._data

        for k in keys[:-1]:
            if k not in d or not isinstance(d[k], dict):
                d[k] = {}
            d = d[k]

        d[keys[-1]] = self._convert_value(value)

    def to(self, model: type[T] | str) -> T:
        """
        Конвертирует данные конфигурации в объект указанной модели.

        :param model: Класс модели или строка с путем к классу.
        :return: Экземпляр модели, инициализированный данными конфигурации.
        """
        if isinstance(model, str):
            module_name, class_name = model.rsplit('.', 1)
            module = importlib.import_module(module_name)
            model_type = getattr(module, class_name)
        else:
            model_type = model
        return model_type(**self._data)

    def _convert_value(self, value: Any) -> Any:
        """
        Преобразует значение: словарь в YampycNode, список словарей в список YampycNode.

        :param value: Значение для преобразования.
        :return: Преобразованное значение.
        """
        if isinstance(value, dict):
            return YampycNode(value)
        elif isinstance(value, list):
            return [YampycNode(item) if isinstance(item, dict) else item for item in value]
        return value

    def __eq__(self, other: Any) -> bool:
        """
        Сравнивает YampycNode с другим объектом.
        Поддерживается сравнение со словарями и списками.

        :param other: Объект для сравнения.
        :return: True, если объекты равны.
        """
        if isinstance(other, YampycNode):
            return self._data == other._data
        elif isinstance(other, dict):
            return self._data == other
        elif isinstance(other, list):
            return self._data == other
        return False

    def __repr__(self) -> str:
        """
        Возвращает строковое представление YampycNode.
        """
        return f'YampycNode({self._data})'


class Yampyc(YampycNode):
    """
    Класс, представляющий конфигурацию YAMPYC.
    Наследует функциональность YampycNode и добавляет методы для работы с источниками данных.
    """

    def __init__(self, data: dict[str, Any] | None = None) -> None:
        """
        Инициализация конфигурации YAMPYC.

        :param data: Словарь с данными конфигурации. Если не указан, используется пустой словарь.
        """
        if data is None:
            data = {}
        super().__init__(data)

    def add_yaml_source(self, file_path: str) -> None:
        """
        Добавляет данные конфигурации из YAML файла с поддержкой переменных окружения.

        :param file_path: Путь к YAML файлу.
        """
        with open(file_path, 'rb') as file:  # Изменено на бинарный режим
            binary_content = file.read()
            try:
                text_content = binary_content.decode('utf-8')
            except UnicodeDecodeError as e:
                raise UnicodeDecodeError(
                    'utf-8',  # encoding
                    binary_content,  # object
                    e.start,  # start
                    e.end,  # end
                    f'Ошибка декодирования файла {file_path}: {e}',
                ) from e
            config = yaml.safe_load(text_content)
            self._data.update(config)

    def add_env_source(self, file_path: str | None = None) -> None:
        """
        Добавляет данные конфигурации из .env файла.

        :param file_path: Путь к .env файлу. Если не указан, используется файл по умолчанию.
        """
        # load_dotenv может работать с текстовыми файлами, но если требуется, можно модифицировать
        # его поведение. Однако чаще всего .env файлы в UTF-8, так что проблем не должно быть.
        load_dotenv(dotenv_path=file_path)
        env_vars = {key: value for key, value in os.environ.items() if key.isupper()}
        self._data.update(env_vars)

    def get(self, key: str, value_type: type[Any] = str) -> Any:
        """
        Получает значение параметра конфигурации с проверкой типа.

        :param key: Имя параметра.
        :param value_type: Ожидаемый тип значения.
        :return: Значение параметра.
        :raises KeyError: Если параметр не найден.
        :raises ValueError: Если значение параметра не соответствует ожидаемому типу.
        """
        value = self._data.get(key)
        if value is None:
            raise KeyError(f"Key '{key}' not found in the configuration")
        try:
            return value_type(value)
        except (ValueError, TypeError):
            raise ValueError(f"Value for key '{key}' is not of type {value_type}")

    def set(self, key: str, value: Any) -> None:
        """
        Устанавливает значение параметра конфигурации.

        :param key: Имя параметра.
        :param value: Значение параметра.
        """
        self._data[key] = value

    def resolve_templates(self) -> None:
        """
        Рекурсивно обходит конфигурационные данные и обрабатывает все шаблоны.

        Этот метод выполняет второй проход по ранее загруженной конфигурации, заменяя все
        шаблоны в формате `${{ action:parameters }}` на соответствующие значения. Поддерживаются
        следующие действия:

        - **env**: Вставка значения переменной окружения.
        Синтаксис: `${{ env:VARIABLE_NAME[:DEFAULT_VALUE] }}`.
        Если переменная окружения `VARIABLE_NAME` не установлена и значение по умолчанию
        `DEFAULT_VALUE` не указано, вызывается исключение `ValueError`.

        - **file**: Вставка содержимого текстового файла.
        Синтаксис: `${{ file:PATH_TO_FILE }}`.
        Если файл по пути `PATH_TO_FILE` не найден, вызывается исключение `FileNotFoundError`.

        - **config**: Вставка значения из текущей конфигурации.
        Синтаксис: `${{ config:PATH.TO.NODE }}`.
        Если указанный путь `PATH.TO.NODE` не найден в конфигурации, вызывается исключение `KeyError`.

        - **yaml**: Загрузка и вставка внешнего YAML файла.
        Синтаксис: `${{ yaml:PATH_TO_YAML_FILE }}`.
        Если файл по пути `PATH_TO_YAML_FILE` не найден, вызывается исключение `FileNotFoundError`.

        Метод обрабатывает шаблоны в строковых значениях конфигурации. Если результат замены
        также является строкой, содержащей шаблоны, обработка повторяется рекурсивно до полного
        разрешения всех шаблонов.

        Пример использования:

        ```yaml
        database:
            user: ${{ env:DB_USER }}
            password: ${{ env:DB_PASSWORD:default_password }}
            init_script: ${{ file:./scripts/init.sql }}
        app:
            db_url: "postgresql://${{ config:database.user }}:${{ config:database.password }}@localhost:5432/app_db"
            extra_settings: ${{ yaml:./configs/extra.yaml }}
        ```

        После вызова `resolve_templates()` все шаблоны в конфигурации будут заменены на реальные значения.

        :raises ValueError:
            - Если в шаблоне указано неизвестное действие.
            - Если переменная окружения не задана и не имеет значения по умолчанию.
            - Если шаблон `config` внутри строки возвращает значение типа `dict` или `list`.
            - Если попытаться использовать шаблон `yaml` внутри строки.

        :raises KeyError:
            - Если указанный ключ не найден в конфигурации при использовании действия `config`.

        :raises FileNotFoundError:
            - Если файл не найден при использовании действий `file` или `yaml`.

        :return: None. Метод изменяет состояние объекта, обновляя конфигурационные данные.
        """
        self._data = self._resolve_node(self._data)

    def _resolve_node(self, node: Any) -> Any:
        if isinstance(node, dict):
            return {k: self._resolve_node(v) for k, v in node.items()}
        elif isinstance(node, list):
            return [self._resolve_node(v) for v in node]
        elif isinstance(node, str):
            new_value = self._resolve_value(node)
            while isinstance(new_value, str) and new_value != node:
                node = new_value
                new_value = self._resolve_value(node)
            return new_value
        else:
            return node

    def _resolve_value(self, value: str) -> Any:
        match = TEMPLATE_PATTERN.fullmatch(value.strip())
        if match:
            action = match.group(1)
            params = match.group(2)
            if action == 'env':
                return self._handle_env(params)
            elif action == 'file':
                return self._handle_file(params)
            elif action == 'config':
                return self._handle_config(params)
            elif action == 'yaml':
                return self._handle_yaml(params)
            else:
                raise ValueError(f'Неизвестное действие в шаблоне: {action}')
        else:
            # Replace any embedded templates within the string
            def replace_match(match: re.Match[str]) -> str:
                action = match.group(1)
                params = match.group(2)
                if action == 'env':
                    return self._handle_env(params)
                elif action == 'file':
                    return self._handle_file(params)
                elif action == 'config':
                    value = self._handle_config(params)
                    if isinstance(value, dict | list):
                        raise ValueError('Шаблон config не может возвращать dict или list внутри строки.')
                    return str(value)
                elif action == 'yaml':
                    raise ValueError('Шаблон yaml не может быть использован внутри строки.')
                else:
                    raise ValueError(f'Неизвестное действие в шаблоне: {action}')

            return TEMPLATE_PATTERN.sub(replace_match, value)

    # Реализация методов обработки для каждого действия
    def _handle_env(self, params: str) -> str:
        # Разбиваем только по первому двоеточию
        if ':' in params:
            var_name, default_value = params.split(':', 1)
            var_name = var_name.strip()
            default_value = default_value.strip()
        else:
            var_name = params.strip()
            default_value = None

        value = os.getenv(var_name, default_value)
        if value is None:
            raise ValueError(f'Переменная окружения {var_name} не задана и не имеет значения по умолчанию.')
        return value

    def _handle_file(self, params: str) -> str:
        file_path = params.strip()
        try:
            with open(file_path, 'rb') as f:  # Изменено на бинарный режим
                binary_content = f.read()
                try:
                    return binary_content.decode('utf-8')
                except UnicodeDecodeError as e:
                    raise UnicodeDecodeError(
                        'utf-8',  # encoding
                        binary_content,  # object
                        e.start,  # start
                        e.end,  # end
                        f'Ошибка декодирования файла {file_path}: {e}',
                    ) from e
        except FileNotFoundError as e:
            raise FileNotFoundError(f'Файл не найден: {file_path}') from e

    def _handle_config(self, params: str) -> Any:
        config_path = params.strip()
        keys = config_path.split('.')
        value = self._data
        for key in keys:
            if key not in value:
                raise KeyError(f"Ключ '{config_path}' не найден в конфигурации.")
            value = value[key]
        return value

    def _handle_yaml(self, params: str) -> Any:
        file_path = params.strip()
        try:
            with open(file_path, 'rb') as f:  # Изменено на бинарный режим
                binary_content = f.read()
                try:
                    text_content = binary_content.decode('utf-8')
                except UnicodeDecodeError as e:
                    raise UnicodeDecodeError(
                        'utf-8',  # encoding
                        binary_content,  # object
                        e.start,  # start
                        e.end,  # end
                        f'Ошибка декодирования файла {file_path}: {e}',
                    ) from e
                yaml_content = yaml.safe_load(text_content)
                # После загрузки внешнего YAML файла, необходимо также обработать его шаблоны
                return self._resolve_node(yaml_content)
        except FileNotFoundError as e:
            raise FileNotFoundError(f'YAML файл не найден: {file_path}') from e


class YampycFactory:
    """
    Фабрика для создания и управления синглтонами конфигурации YAMPYC.
    """

    _instances: dict[str, Yampyc] = {}

    @classmethod
    def get_config(cls, key: str = 'default') -> Yampyc:
        """
        Возвращает экземпляр конфигурации для указанного ключа.
        Если экземпляр не существует, создается новый.

        :param key: Ключ конфигурации. По умолчанию "default".
        :return: Экземпляр Yampyc.
        """
        if key not in cls._instances:
            cls._instances[key] = Yampyc()
        return cls._instances[key]

    @classmethod
    def set_config(cls, config: Yampyc, key: str = 'default') -> None:
        """
        Устанавливает экземпляр конфигурации для указанного ключа.

        :param config: Экземпляр Yampyc.
        :param key: Ключ конфигурации. По умолчанию "default".
        """
        cls._instances[key] = config
