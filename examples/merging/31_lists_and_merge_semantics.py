"""List merge semantics: lists are replaced, not merged per item.

Run:
    PYTHONPATH=src uv run python examples/merging/31_lists_and_merge_semantics.py
"""

from __future__ import annotations

from coyaml import YSettings


def main() -> None:
    base = {'features': ['a', 'b']}
    override = {'features': ['c']}

    cfg = YSettings(base)
    cfg2 = YSettings(override)

    # Emulate merge as done by add_source: the latest source replaces the list
    cfg._data.update(cfg2._data)  # for demonstration; add_source would do a deep merge for dicts only

    print('features =', cfg['features'])  # ['c']


if __name__ == '__main__':
    main()
