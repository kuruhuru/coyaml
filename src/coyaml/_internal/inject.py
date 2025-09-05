"""Utilities for dependency injection."""

from __future__ import annotations

import inspect
from functools import wraps
from typing import Annotated, Any, get_args, get_origin, get_type_hints

try:  # Prefer typing_extensions on 3.10 to preserve Annotated extras
    from typing import get_type_hints as get_type_hints_extras
except Exception:  # pragma: no cover
    get_type_hints_extras = get_type_hints  # fallback to stdlib


from coyaml._internal.node import YList, YNode
from coyaml._internal.registry import YRegistry
from coyaml._internal.search import _dotted, _iter_tree, find_by_name, find_by_path_suffix


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
                                    similar_by_name: list[str] = []
                                    for segs, _value in _iter_tree(cfg_dict):
                                        if segs and name in segs:
                                            similar_by_name.append(_dotted(segs))
                                            if len(similar_by_name) >= 5:
                                                break
                                    details = f'masks={masks!r}'
                                    if similar_by_name:
                                        details += '. Similar: ' + ', '.join(similar_by_name)
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
                                    value = YList([YNode(v) if isinstance(v, dict) else v for v in value])
                            else:
                                # If path is provided, support relative suffix lookup unless absolute
                                masks = (
                                    [decorator_mask] if isinstance(decorator_mask, str) else (decorator_mask or None)
                                )
                                if path.startswith('^'):
                                    absolute = path[1:]
                                    value = cfg[absolute]
                                else:
                                    cfg_dict = cfg.to_dict()
                                    matches = find_by_path_suffix(cfg_dict, path, masks)
                                    if not matches:
                                        # Handle Optional/default None
                                        is_optional = False
                                        args = get_args(typ)
                                        if args and type(None) in args:
                                            is_optional = True
                                        default_is_none = (
                                            name in sig.parameters and sig.parameters[name].default is None
                                        )
                                        if is_optional or default_is_none:
                                            bound.arguments[name] = None
                                            break
                                        # Diagnostics with similar paths containing the last segment of suffix
                                        segs = path.split('.')
                                        last = segs[-1] if segs else ''
                                        cfg_dict2 = cfg.to_dict()
                                        similar_by_suffix: list[str] = []
                                        for seg_path, _value in _iter_tree(cfg_dict2):
                                            if seg_path and last in seg_path:
                                                similar_by_suffix.append(_dotted(seg_path))
                                                if len(similar_by_suffix) >= 5:
                                                    break
                                        details = f"path='{path}', masks={masks!r}"
                                        if similar_by_suffix:
                                            details += '. Similar: ' + ', '.join(similar_by_suffix)
                                        raise KeyError(f'Key by relative path suffix not found ({details})')

                                    if len(matches) > 1 and decorator_unique:
                                        listed = ', '.join(p for p, _ in matches[:5])
                                        more = '...' if len(matches) > 5 else ''
                                        raise KeyError(
                                            f"Ambiguous relative path suffix '{path}' (masks={masks!r}): {listed}{more}. "
                                            f'Specify absolute path (^prefix) or restrict mask.'
                                        )

                                    found_path, raw_value = matches[0]
                                    value = raw_value
                                    if isinstance(value, dict):
                                        value = YNode(value)
                                    elif isinstance(value, list):
                                        value = YList([YNode(v) if isinstance(v, dict) else v for v in value])
                            if isinstance(value, YNode | YList):
                                # Конвертируем во всё, что не включает YNode
                                candidates = get_args(typ) if get_args(typ) else (typ,)
                                if YNode in candidates or typ is YNode:
                                    pass
                                else:
                                    value = value.to(typ)
                            bound.arguments[name] = value
                            break
            return func(*bound.args, **bound.kwargs)

        return wrapper

    if _func is None:
        return _decorate
    else:
        return _decorate(_func)
