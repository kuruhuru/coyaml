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

# Pattern for variable name placeholders
TEMPLATE_PATTERN = re.compile(r'\${{\s*(\w+):(.+?)}}')


# Type variable used in the ``to`` method
T = TypeVar('T', bound='BaseModel')


class YampycNode:
    """Represents a configuration node.

    Allows access to nested configuration parameters via attributes and keys.
    """

    def __init__(self, data: dict[str, Any]):
        """
        Initialize the configuration node.

        :param data: Dictionary containing configuration data.
        """
        self._data = data

    def to_dict(self) -> dict[str, Any]:
        """Convert the configuration node to a dictionary."""
        return self._data

    def __iter__(self) -> Iterator[str]:
        """Iterate over configuration keys."""
        return iter(self._data)

    def items(self) -> Iterator[tuple[str, Any]]:
        """Iterate over configuration key/value pairs like a dictionary."""
        return self._data.items()  # type: ignore

    def values(self) -> Any:
        """Iterate over configuration values."""
        return self._data.values()

    def __getattr__(self, item: str) -> Any:
        """Access configuration parameters via attributes.

        :param item: Parameter name.
        :return: Parameter value or a new node if the value is a dictionary.
        :raises AttributeError: If the parameter is missing.
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
        """Access parameters using keys with dot notation.

        :param item: Parameter name or dot separated path.
        :return: Parameter value.
        :raises KeyError: If the parameter is not found.
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
        """Set a configuration value via attributes.

        :param key: Parameter name.
        :param value: Parameter value.
        """
        if key == '_data':  # special case for the internal attribute
            super().__setattr__(key, value)
        else:
            self._data[key] = self._convert_value(value)

    def __setitem__(self, key: str, value: Any) -> None:
        """Set a configuration value via keys. Dot notation is supported.

        :param key: Parameter name or dot separated path.
        :param value: Parameter value.
        """
        keys = key.split('.')
        d = self._data

        for k in keys[:-1]:
            if k not in d or not isinstance(d[k], dict):
                d[k] = {}
            d = d[k]

        d[keys[-1]] = self._convert_value(value)

    def to(self, model: type[T] | str) -> T:
        """Convert configuration data to an instance of the given model.

        :param model: Model class or dotted path to the class.
        :return: Instance of the model initialised with configuration data.
        """
        if isinstance(model, str):
            module_name, class_name = model.rsplit('.', 1)
            module = importlib.import_module(module_name)
            model_type = getattr(module, class_name)
        else:
            model_type = model
        return model_type(**self._data)

    def _convert_value(self, value: Any) -> Any:
        """Convert dictionaries and lists of dictionaries into ``YampycNode`` objects.

        :param value: Value to convert.
        :return: Converted value.
        """
        if isinstance(value, dict):
            return YampycNode(value)
        elif isinstance(value, list):
            return [YampycNode(item) if isinstance(item, dict) else item for item in value]
        return value

    def __eq__(self, other: Any) -> bool:
        """Compare ``YampycNode`` with another object.

        Dictionaries and lists are also supported.

        :param other: Object to compare with.
        :return: ``True`` if the objects are equal.
        """
        if isinstance(other, YampycNode):
            return self._data == other._data
        elif isinstance(other, dict):
            return self._data == other
        elif isinstance(other, list):
            return self._data == other
        return False

    def __repr__(self) -> str:
        """Return string representation of ``YampycNode``."""
        return f'YampycNode({self._data})'


class Yampyc(YampycNode):
    """
    Main configuration class.
    Inherits functionality from ``YampycNode`` and provides helpers for working with data sources.
    """

    def __init__(self, data: dict[str, Any] | None = None) -> None:
        """
        Initialize the YAMPYC configuration.

        :param data: Dictionary with configuration data. Defaults to an empty dictionary.
        """
        if data is None:
            data = {}
        super().__init__(data)

    def add_yaml_source(self, file_path: str) -> None:
        """Add configuration data from a YAML file with environment variable support.

        :param file_path: Path to the YAML file.
        """
        with open(file_path, 'rb') as file:  # open in binary mode
            binary_content = file.read()
            try:
                text_content = binary_content.decode('utf-8')
            except UnicodeDecodeError as e:
                raise UnicodeDecodeError(
                    'utf-8',  # encoding
                    binary_content,  # object
                    e.start,  # start
                    e.end,  # end
                    f'Failed to decode file {file_path}: {e}',
                ) from e
            config = yaml.safe_load(text_content)
            self._data.update(config)

    def add_env_source(self, file_path: str | None = None) -> None:
        """Add configuration data from a ``.env`` file.

        :param file_path: Path to the ``.env`` file. If omitted, the default file is used.
        """
        # ``load_dotenv`` works with text files; most ``.env`` files are UTF-8 so there should be no issues.
        load_dotenv(dotenv_path=file_path)
        env_vars = {key: value for key, value in os.environ.items() if key.isupper()}
        self._data.update(env_vars)

    def get(self, key: str, value_type: type[Any] = str) -> Any:
        """Retrieve a configuration value with type checking.

        :param key: Parameter name.
        :param value_type: Expected type.
        :return: Parameter value.
        :raises KeyError: If the parameter does not exist.
        :raises ValueError: If the value cannot be cast to ``value_type``.
        """
        value = self._data.get(key)
        if value is None:
            raise KeyError(f"Key '{key}' not found in the configuration")
        try:
            return value_type(value)
        except (ValueError, TypeError):
            raise ValueError(f"Value for key '{key}' is not of type {value_type}")

    def set(self, key: str, value: Any) -> None:
        """Set a configuration value.

        :param key: Parameter name.
        :param value: Parameter value.
        """
        self._data[key] = value

    def resolve_templates(self) -> None:
        """Recursively resolve all template expressions in the configuration.

        Templates of the form ``${{ action:parameters }}`` are replaced with the
        corresponding values. Supported actions are ``env``, ``file``, ``config``
        and ``yaml``. Templates inside strings are processed repeatedly until no
        placeholders remain.

        :raises ValueError: unknown action or invalid template usage.
        :raises KeyError: referenced key is missing when using ``config``.
        :raises FileNotFoundError: file referenced in ``file`` or ``yaml`` is missing.
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
            with open(file_path, 'rb') as f:  # open in binary mode
                binary_content = f.read()
                try:
                    return binary_content.decode('utf-8')
                except UnicodeDecodeError as e:
                    raise UnicodeDecodeError(
                        'utf-8',  # encoding
                        binary_content,  # object
                        e.start,  # start
                        e.end,  # end
                        f'Failed to decode file {file_path}: {e}',
                    ) from e
        except FileNotFoundError as e:
            raise FileNotFoundError(f'File not found: {file_path}') from e

    def _handle_config(self, params: str) -> Any:
        config_path = params.strip()
        keys = config_path.split('.')
        value = self._data
        for key in keys:
            if key not in value:
                raise KeyError(f"Key '{config_path}' not found in the configuration")
            value = value[key]
        return value

    def _handle_yaml(self, params: str) -> Any:
        file_path = params.strip()
        try:
            with open(file_path, 'rb') as f:  # open in binary mode
                binary_content = f.read()
                try:
                    text_content = binary_content.decode('utf-8')
                except UnicodeDecodeError as e:
                    raise UnicodeDecodeError(
                        'utf-8',  # encoding
                        binary_content,  # object
                        e.start,  # start
                        e.end,  # end
                        f'Failed to decode file {file_path}: {e}',
                    ) from e
                yaml_content = yaml.safe_load(text_content)
                # After loading an external YAML file its templates must also be resolved
                return self._resolve_node(yaml_content)
        except FileNotFoundError as e:
            raise FileNotFoundError(f'YAML file not found: {file_path}') from e


class YampycFactory:
    """Factory for creating and managing configuration singletons."""

    _instances: dict[str, Yampyc] = {}

    @classmethod
    def get_config(cls, key: str = 'default') -> Yampyc:
        """Return a configuration instance for the given key.

        If it does not exist a new instance is created.

        :param key: Configuration key. Defaults to ``"default"``.
        :return: ``Yampyc`` instance.
        """
        if key not in cls._instances:
            cls._instances[key] = Yampyc()
        return cls._instances[key]

    @classmethod
    def set_config(cls, config: Yampyc, key: str = 'default') -> None:
        """Set a configuration instance for the given key.

        :param config: ``Yampyc`` instance.
        :param key: Configuration key. Defaults to ``"default"``.
        """
        cls._instances[key] = config
