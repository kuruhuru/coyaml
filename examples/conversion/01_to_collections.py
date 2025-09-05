"""Conversion of YNode to typed collections.

Run:
    PYTHONPATH=src uv run python examples/conversion/01_to_collections.py
"""

from __future__ import annotations

from pydantic import BaseModel

from coyaml import YNode


class BModel(BaseModel):
    name: str
    enabled: bool | None = None


def main() -> None:
    cfg = YNode(
        {
            'services': {
                's1': {'name': 'alpha', 'enabled': 1},
                's2': {'name': 'beta'},
            },
            'flags': {'x': 1, 'y': 'yes', 'z': False},
            'items': [{'name': 'a'}, {'name': 'b', 'enabled': False}],
        }
    )

    services = cfg['services'].to(dict[str, BModel])
    print('services types:', {k: type(v).__name__ for k, v in services.items()})
    print('services s1:', services['s1'])

    flags = cfg['flags'].to(dict[str, bool])
    print('flags:', flags)

    items = cfg['items'].to(list[BModel])
    print('items:', [m.model_dump() for m in items])


if __name__ == '__main__':
    main()
