import os
from pathlib import Path
from typing import Annotated

from pydantic import BaseModel

from coyaml import YResource, coyaml
from coyaml._internal.config import YSettings
from coyaml._internal.node import YNode
from coyaml._internal.registry import YRegistry
from coyaml.sources.yaml import YamlFileSource


def load_config(path: str) -> None:
    os.environ['DB_USER'] = 'test_user'
    os.environ['DB_PASSWORD'] = 'test_password'  # noqa: S105

    config = YSettings()
    config.add_source(YamlFileSource(path))
    config.resolve_templates()
    YRegistry.set_config(config)


# Load example config located next to this file
EXAMPLES_DIR = Path(__file__).resolve().parent
load_config((EXAMPLES_DIR / 'config' / 'config.yaml').as_posix())


@coyaml
def function_with_basic_types(
    x: Annotated[int | None, YResource('index')] = None,
    y: Annotated[bool | None, YResource('stream')] = None,
    z: Annotated[str | None, YResource('llm')] = None,
) -> tuple[int | None, bool | None, str | None]:
    """Return x, y and z values."""
    return x, y, z


class DBConfig(BaseModel):
    url: str
    user: str
    password: str
    init_script: str


@coyaml
def function_with_complex_types(
    db: Annotated[DBConfig | None, YResource('debug.db')] = None,
    db_node: Annotated[YNode | None, YResource('debug.db')] = None,
) -> tuple[DBConfig | None, YNode | None]:
    """Return db config."""
    return db, db_node


def _test_basic_types() -> None:
    result = function_with_basic_types()
    assert result == (9, True, 'path/to/llm/config')  # noqa: S101
    result = function_with_basic_types(x=11)
    assert result == (11, True, 'path/to/llm/config')  # noqa: S101


def _test_pydantic_model() -> None:
    db, db_node = function_with_complex_types()
    assert isinstance(db, DBConfig)  # noqa: S101
    assert isinstance(db_node, YNode)  # noqa: S101
    db1 = YRegistry.get_config().debug.db.to(DBConfig)
    assert db == db1  # noqa: S101


if __name__ == '__main__':
    _test_basic_types()
    _test_pydantic_model()
