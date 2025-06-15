import os
from collections.abc import Callable
from typing import Annotated

from coyaml import ConfigKey, coyaml
from coyaml._internal.registry import YRegistry


@coyaml
def function_with_basic_types1(
    x: Annotated[int, ConfigKey('index')],
    y: Annotated[
        bool,
        ConfigKey('stream'),
    ],
    z: Annotated[
        str,
        ConfigKey('llm'),
    ],
) -> tuple[int, bool, str]:
    """Return x, y and z values."""
    return x, y, z


def test_basic_types(
    load_config: Callable[[str], None], function_with_basic_types: Callable[..., tuple[int, bool, str]]
) -> None:
    os.environ['DB_USER'] = 'test_user'
    os.environ['DB_PASSWORD'] = 'test_password'  # noqa: S105

    load_config('tests/config/config.yaml')
    result = function_with_basic_types()
    assert result == (9, True, 'path/to/llm/config')
    YRegistry.remove_config()
