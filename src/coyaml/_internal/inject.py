"""Utilities for dependency injection."""

from __future__ import annotations

import inspect
from functools import wraps
from typing import Annotated, Any, get_args, get_origin, get_type_hints

try:  # Prefer typing_extensions on 3.10 to preserve Annotated extras
    from typing import get_type_hints as get_type_hints_extras
except Exception:  # pragma: no cover
    get_type_hints_extras = get_type_hints  # fallback to stdlib

from pydantic import BaseModel

from coyaml._internal.node import YNode
from coyaml._internal.registry import YRegistry
from coyaml._internal.search import _dotted, _iter_tree, find_by_name


class YResource:
    """Metadata for injecting a value from :class:`YSettings`."""

    def __init__(self, path: str | None = None, config: str = 'default') -> None:
        self.path = path
        self.config = config


def coyaml(_func=None, *, mask: str | list[str] | None = None, unique: bool = True):  # type: ignore
    """Decorator that injects parameters based on ``Annotated`` hints.

    Supports both usages:
        @coyaml
        def f(...): ...

        @coyaml(mask='**.user', unique=True)
        def g(...): ...
    """

    decorator_mask = mask
    decorator_unique = unique

    def _decorate(func: Any) -> Any:
        # Use typing_extensions.get_type_hints when available to preserve Annotated extras on 3.10
        hints = get_type_hints_extras(func, include_extras=True)
        sig = inspect.signature(func)

        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            bound = sig.bind_partial(*args, **kwargs)
            for name, _param in sig.parameters.items():
                if name in bound.arguments:
                    continue

                hint = hints.get(name)
                # Fallback: Python 3.10 get_type_hints(include_extras=True) may "lose"
                # Annotated metadata (only base type is returned). If so, try to
                # fetch the raw annotation directly from the signature.
                if hint is None or get_origin(hint) is not Annotated:
                    # Fallback 1: evaluated annotations (handles future annotations)
                    evaluated = inspect.get_annotations(func, eval_str=True)
                    raw = evaluated.get(name, _param.annotation)
                    if get_origin(raw) is Annotated:
                        hint = raw

                if hint is None:
                    continue

                if get_origin(hint) is Annotated:
                    typ, *meta = get_args(hint)
                    for m in meta:
                        if isinstance(m, YResource):
                            cfg = YRegistry.get_config(m.config)
                            path = m.path
                            if path is None:
                                masks = (
                                    [decorator_mask] if isinstance(decorator_mask, str) else (decorator_mask or None)
                                )
                                cfg_dict = cfg.to_dict()
                                matches = find_by_name(cfg_dict, name, masks)
                                if not matches:
                                    # If Optional or default is None — return None, otherwise raise
                                    is_optional = False
                                    args = get_args(typ)
                                    if args and type(None) in args:
                                        is_optional = True
                                    default_is_none = name in sig.parameters and sig.parameters[name].default is None
                                    if is_optional or default_is_none:
                                        bound.arguments[name] = None
                                        break
                                    # Gather a few similar paths containing the parameter name
                                    similar: list[str] = []
                                    for segs, _value in _iter_tree(cfg_dict):
                                        if segs and name in segs:
                                            similar.append(_dotted(segs))
                                            if len(similar) >= 5:
                                                break
                                    details = f'masks={masks!r}'
                                    if similar:
                                        details += '. Similar: ' + ', '.join(similar)
                                    raise KeyError(f"Key by name '{name}' not found ({details})")

                                if len(matches) > 1 and decorator_unique:
                                    listed = ', '.join(p for p, _ in matches[:5])
                                    more = '...' if len(matches) > 5 else ''
                                    raise KeyError(
                                        f"Ambiguous key name '{name}' (masks={masks!r}): {listed}{more}. "
                                        f'Specify explicit path or restrict mask.'
                                    )

                                # Take the first candidate in deterministic order
                                found_path, raw_value = matches[0]
                                value = raw_value
                                if isinstance(value, dict):
                                    value = YNode(value)
                                elif isinstance(value, list):
                                    value = [YNode(v) if isinstance(v, dict) else v for v in value]
                            else:
                                value = cfg[path]
                            if isinstance(value, YNode):
                                # If the value is a YNode but the annotation expects some
                                # other type, convert using YNode.to(). We skip conversion
                                # when the annotation explicitly includes YNode itself
                                # (so users can opt-out of automatic casting).
                                candidates = get_args(typ) if get_args(typ) else (typ,)

                                # When annotation allows YNode, leave as-is
                                if YNode in candidates or typ is YNode:
                                    pass  # не конвертируем
                                else:
                                    # Find the first candidate type that is subclass(BaseModel) for conversion
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

    if _func is None:
        return _decorate
    else:
        return _decorate(_func)
