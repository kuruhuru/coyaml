import os
from typing import Annotated

from coyaml import YResource, YSettings, coyaml
from coyaml._internal.registry import YRegistry
from coyaml.sources.yaml import YamlFileSource


def load_config(path: str) -> None:
    config = YSettings()
    config.add_source(YamlFileSource(path))
    config.resolve_templates()
    YRegistry.set_config(config)


@coyaml
def function_with_basic_types1(
    a: str,
    x: Annotated[int | None, YResource('index')] = None,
    y: Annotated[
        bool | None,
        YResource('stream'),
    ] = None,
    z: Annotated[
        str | None,
        YResource('llm'),
    ] = None,
) -> tuple[str, int | None, bool | None, str | None]:
    """Return a, x, y and z values."""
    return a, x, y, z


def test_basic_types() -> None:
    os.environ['DB_USER'] = 'test_user'
    os.environ['DB_PASSWORD'] = 'test_password'  # noqa: S105

    load_config('tests/config/config.yaml')
    result = function_with_basic_types1(a='test_user')
    assert result == ('test_user', 9, True, 'path/to/llm/config')  # noqa: S101
    YRegistry.remove_config()


if __name__ == '__main__':
    test_basic_types()
