"""Search utilities for configuration trees with glob masks on dotted paths.

Supported masks:
- `*` — exactly one path segment (no dot inside)
- `**` — zero or more segments

Paths are represented as ``a.b.0.c`` — list elements are addressed by indices.
"""

from __future__ import annotations

import re
from collections.abc import Iterator, Sequence
from typing import Any


def _iter_tree(obj: Any, prefix: list[str] | None = None) -> Iterator[tuple[list[str], Any]]:
    """Depth-first traversal over dicts/lists, yields (path_segments, value).

    Emits entries for both leaf values and intermediate dict/list nodes.
    """
    path: list[str] = [] if prefix is None else prefix
    if isinstance(obj, dict):
        for key, value in obj.items():
            current = [*path, str(key)]
            # emit the node itself
            yield current, value
            # then descend if composite
            if isinstance(value, dict | list):
                yield from _iter_tree(value, current)
    elif isinstance(obj, list):
        for idx, value in enumerate(obj):
            current = [*path, str(idx)]
            # emit the node itself
            yield current, value
            # then descend if composite
            if isinstance(value, dict | list):
                yield from _iter_tree(value, current)
    else:
        # root scalar
        yield path, obj


def _dotted(path: Sequence[str]) -> str:
    return '.'.join(path)


def _compile_mask(mask: str) -> re.Pattern[str]:
    r"""Compile a glob-like mask for dotted paths into a regex.

    Examples:
      - "**.user" -> r"^(?:[^.]+(?:\.[^.]+)*)?\.user$"
      - "debug.*.user" -> r"^debug\.[^.]+\.user$"
    """
    segments = mask.split('.') if mask else []
    regex_parts: list[str] = ['^']
    prev_was_globstar = False
    for i, seg in enumerate(segments):
        if seg == '**':
            if i == 0:
                # Zero or more segments from the beginning
                regex_parts.append(r'(?:[^.]+(?:\.[^.]+)*)?')
            else:
                # Zero or more additional dotted segments
                regex_parts.append(r'(?:\.[^.]+)*')
            prev_was_globstar = True
            continue
        # Non-globstar segment
        if seg == '*':
            if i > 0:
                regex_parts.append(r'(?:\.)?' if prev_was_globstar else r'\.')
            regex_parts.append(r'[^.]+')
        else:
            if i > 0:
                regex_parts.append(r'(?:\.)?' if prev_was_globstar else r'\.')
            regex_parts.append(re.escape(seg))
        prev_was_globstar = False
    regex_parts.append('$')
    pattern = ''.join(regex_parts)
    return re.compile(pattern)


def _match_any_mask(path: str, masks: Sequence[str] | None) -> bool:
    if not masks:
        return True
    for m in masks:
        if _compile_mask(m).match(path):
            return True
    return False


def find_by_name(
    data: dict[str, Any],
    name: str,
    masks: Sequence[str] | None = None,
) -> list[tuple[str, Any]]:
    """Find all values whose last path segment equals ``name``.

    Returns list of tuples (full dotted path, value). Order is deterministic:
    pre-order following the original key/element order. Masks, if provided,
    filter by full dotted path.
    """
    results: list[tuple[str, Any]] = []
    for path_list, value in _iter_tree(data):
        if not path_list:
            continue
        if path_list[-1] != name:
            continue
        dotted = _dotted(path_list)
        if _match_any_mask(dotted, masks):
            results.append((dotted, value))
    return results


def find_by_path_suffix(
    data: dict[str, Any],
    suffix: str,
    masks: Sequence[str] | None = None,
) -> list[tuple[str, Any]]:
    """Find all values whose dotted path ends with the given ``suffix``.

    Examples:
      - suffix="a.b.c" matches "root.x.a.b.c" and "a.b.c"
      - masks, if provided, filter candidates by full dotted path first

    Returns list of tuples (full dotted path, value). Order is deterministic
    (pre-order of the original structure).
    """
    # Normalize suffix into segments and strip leading/trailing dots
    trimmed = suffix.strip('.')
    suffix_segments = trimmed.split('.') if trimmed else []

    results: list[tuple[str, Any]] = []
    for path_list, value in _iter_tree(data):
        if not path_list:
            continue
        dotted = _dotted(path_list)
        if not _match_any_mask(dotted, masks):
            continue
        # Fast path: if suffix equals full path
        if dotted.endswith(trimmed):
            # Validate proper segment suffix match (not partial segment)
            if not trimmed:
                continue
            # Ensure segment alignment: compare as segments to avoid partial matches
            if len(suffix_segments) <= len(path_list) and path_list[-len(suffix_segments) :] == suffix_segments:
                results.append((dotted, value))
                continue
        else:
            # If endwith failed (e.g., due to segment boundary), fallback to segment comparison
            if len(suffix_segments) <= len(path_list) and path_list[-len(suffix_segments) :] == suffix_segments:
                results.append((dotted, value))
    return results
