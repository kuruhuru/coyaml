"""Utilities for dependency injection."""

from __future__ import annotations

import inspect
from functools import wraps
from typing import Annotated, Any, get_args, get_origin, get_type_hints

from pydantic import BaseModel

from coyaml._internal.node import YNode
from coyaml._internal.registry import YRegistry


class YResource:
    """Метаданные для внедрения значения из :class:`YSettings`."""

    def __init__(self, path: str, config: str = 'default') -> None:
        self.path = path
        self.config = config


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
            # Fallback: на Python 3.10 get_type_hints(include_extras=True) может «потерять»
            # метаданные Annotated (возвращается только базовый тип без extras).
            # Поэтому, если hint не содержит Annotated, пробуем взять исходную аннотацию
            # прямо из сигнатуры.
            if hint is None or get_origin(hint) is not Annotated:
                raw_ann = _param.annotation
                if get_origin(raw_ann) is Annotated:
                    hint = raw_ann

            if hint is None:
                continue

            if get_origin(hint) is Annotated:
                typ, *meta = get_args(hint)
                for m in meta:
                    if isinstance(m, YResource):
                        cfg = YRegistry.get_config(m.config)
                        value = cfg[m.path]
                        if isinstance(value, YNode):
                            # If the value is a YNode but the annotation expects some
                            # other type, convert using YNode.to().  We purposefully
                            # skip conversion when the annotation explicitly includes
                            # YNode itself (so users can opt-out of automatic casting).
                            candidates = get_args(typ) if get_args(typ) else (typ,)

                            # Когда аннотация допускает YNode, оставляем как есть
                            if YNode in candidates or typ is YNode:
                                pass  # не конвертируем
                            else:
                                # ищем первый тип-класс-subclass(BaseModel) для конвертации
                                target_type = next(
                                    (c for c in candidates if isinstance(c, type) and issubclass(c, BaseModel)),
                                    None,
                                )

                                if target_type is not None:
                                    value = value.to(target_type)
                        bound.arguments[name] = value
                        break
        return func(*bound.args, **bound.kwargs)

    return wrapper
