"""Working with multiple configuration instances via YRegistry.

Run:
    PYTHONPATH=src uv run python examples/registry/40_registry_get_set_multiple.py
"""

from __future__ import annotations

from coyaml import YRegistry, YSettings


def main() -> None:
    dev = YSettings({'env': 'dev', 'value': 1})
    prod = YSettings({'env': 'prod', 'value': 2})

    YRegistry.set_config(dev, 'dev')
    YRegistry.set_config(prod, 'prod')

    print('dev.value =', YRegistry.get_config('dev')['value'])
    print('prod.value =', YRegistry.get_config('prod')['value'])

    # Clean up
    YRegistry.remove_config('dev')
    YRegistry.remove_config('prod')


if __name__ == '__main__':
    main()
