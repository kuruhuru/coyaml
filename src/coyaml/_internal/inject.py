"""Utilities for dependency injection."""

from __future__ import annotations

import inspect
from functools import wraps
from typing import Annotated, Any, get_args, get_origin, get_type_hints

from pydantic import BaseModel

from coyaml._internal.node import YNode
from coyaml._internal.registry import YRegistry


class ConfigKey:
    """Metadata for injecting a value from :class:`YConfig`."""

    def __init__(self, path: str, key: str = 'default') -> None:
        self.path = path
        self.key = key


class DepName:
    """Metadata for injecting a dependency from :class:`YDeps`."""

    def __init__(self, name: str) -> None:
        self.name = name


def coyaml(func):  # type: ignore
    """Decorator that injects parameters based on ``Annotated`` hints."""

    hints = get_type_hints(func, include_extras=True)
    sig = inspect.signature(func)

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        bound = sig.bind_partial(*args, **kwargs)
        for name, _param in sig.parameters.items():
            if name in bound.arguments:
                continue

            hint = hints.get(name)
            if hint is None:
                continue

            if get_origin(hint) is Annotated:
                typ, *meta = get_args(hint)
                for m in meta:
                    if isinstance(m, ConfigKey):
                        cfg = YRegistry.get_config(m.key)
                        value = cfg[m.path]
                        if isinstance(value, YNode) and isinstance(typ, type) and issubclass(typ, BaseModel):
                            value = value.to(typ)
                        bound.arguments[name] = value
                        break
                    elif isinstance(m, DepName):
                        deps = YRegistry.get_deps()
                        bound.arguments[name] = deps.get(m.name)
                        break
        return func(*bound.args, **bound.kwargs)

    return wrapper
