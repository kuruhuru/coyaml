# src/coyaml/utils/merge.py

from typing import Any


def deep_merge(dest: dict[str, Any], src: dict[str, Any]) -> None:
    """
    Recursively merge src into dest.

    For overlapping keys:
    - If both values are dicts, merge them recursively.
    - Otherwise, src value overrides dest.

    Args:
        dest: Destination dict to be updated in-place.
        src: Source dict whose values overwrite or merge into dest.
    """
    for key, value in src.items():
        if key in dest and isinstance(dest[key], dict) and isinstance(value, dict):
            deep_merge(dest[key], value)
        else:
            dest[key] = value
