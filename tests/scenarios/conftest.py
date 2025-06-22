from collections.abc import Callable
from typing import Annotated

import pytest

from coyaml import YRegistry, YResource, YSettings, coyaml
from coyaml.sources.yaml import YamlFileSource


@pytest.fixture
def load_config() -> Callable[[str], None]:
    """
    Returns a function that loads a config file and registers it in the registry.
    The function can be used as a fixture in tests.
    """

    def _load_config(path: str) -> None:
        config = YSettings()
        config.add_source(YamlFileSource(path))
        config.resolve_templates()
        YRegistry.set_config(config)

    return _load_config


@pytest.fixture
def function_with_basic_types() -> Callable[..., tuple[int, bool, str]]:
    """
    Create a simple function decorated with @coyaml with basic types.
    """

    @coyaml
    def _function_with_basic_types(
        x: Annotated[int, YResource('index')],
        y: Annotated[
            bool,
            YResource('stream'),
        ],
        z: Annotated[
            str,
            YResource('llm'),
        ],
    ) -> tuple[int, bool, str]:
        """Return x, y and z values."""
        return x, y, z

    return _function_with_basic_types
