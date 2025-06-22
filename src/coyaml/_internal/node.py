import importlib
import re
from collections.abc import Iterator
from typing import (
    Any,
    TypeVar,
)

from pydantic import BaseModel

# Pattern for finding variable names
TEMPLATE_PATTERN = re.compile(r'\${{\s*(\w+):(.+?)}}')


# Define type variable
T = TypeVar('T', bound='BaseModel')


class YNode:
    """
    A class representing a configuration node.
    Allows accessing nested configuration parameters through attributes and keys.
    """

    def __init__(self, data: dict[str, Any]):
        """
        Initialize a configuration node.

        :param data: Dictionary with configuration data.
        """
        self._data = data

    def to_dict(self) -> dict[str, Any]:
        """
        Convert the configuration node to a dictionary.
        """
        return self._data

    def __iter__(self) -> Iterator[str]:
        """
        Allow iteration over configuration keys.
        """
        return iter(self._data)

    def items(self) -> Iterator[tuple[str, Any]]:
        """
        Allow iteration over configuration keys and values, like in a dictionary.
        """
        return self._data.items()  # type: ignore

    def values(self) -> Any:
        """
        Allow iteration over configuration values.
        """
        return self._data.values()

    def __getattr__(self, item: str) -> Any:
        """
        Allow accessing configuration parameters through attributes.

        :param item: Parameter name.
        :return: Parameter value or a new configuration node if the parameter is a dictionary.
        :raises AttributeError: If the parameter is not found.
        """
        if item not in self._data:
            raise AttributeError(f"'YNode' object has no attribute '{item}'")
        value = self._data[item]
        if isinstance(value, dict):
            return YNode(value)
        elif isinstance(value, list):
            return [YNode(v) if isinstance(v, dict) else v for v in value]
        return value

    def __getitem__(self, item: str) -> Any:
        """
        Allow accessing configuration parameters through keys using dot notation.

        :param item: Parameter name or chain of parameters separated by dots.
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
            return YNode(value)
        elif isinstance(value, list):
            return [YNode(v) if isinstance(v, dict) else v for v in value]
        return value

    def __setattr__(self, key: str, value: Any) -> None:
        """
        Set a configuration parameter value through attributes.

        :param key: Parameter name.
        :param value: Parameter value.
        """
        if key == '_data':  # Exception for internal attribute
            super().__setattr__(key, value)
        else:
            self._data[key] = self._convert_value(value)

    def __setitem__(self, key: str, value: Any) -> None:
        """
        Set a configuration parameter value through keys.
        Supports setting parameters with dot notation.

        :param key: Parameter name or chain of parameters separated by dots.
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
        """
        Convert configuration data to an object of the specified model.

        :param model: Model class or string with class path.
        :return: Model instance initialized with configuration data.
        """
        if isinstance(model, str):
            module_name, class_name = model.rsplit('.', 1)
            module = importlib.import_module(module_name)
            model_type: type[T] = getattr(module, class_name)
        else:
            model_type = model
        return model_type(**self._data)

    def _convert_value(self, value: Any) -> Any:
        """
        Convert value: dictionary to YNode, list of dictionaries to list of YNode.

        :param value: Value to convert.
        :return: Converted value.
        """
        if isinstance(value, dict):
            return YNode(value)
        elif isinstance(value, list):
            return [YNode(item) if isinstance(item, dict) else item for item in value]
        return value

    def __eq__(self, other: Any) -> bool:
        """
        Compare YNode with another object.
        Supports comparison with dictionaries and lists.

        :param other: Object to compare with.
        :return: True if objects are equal.
        """
        if isinstance(other, YNode):
            return self._data == other._data
        elif isinstance(other, dict):
            return self._data == other
        elif isinstance(other, list):
            return self._data == other
        return False

    def __repr__(self) -> str:
        """
        Return string representation of YNode.
        """
        return f'YNode({self._data})'
