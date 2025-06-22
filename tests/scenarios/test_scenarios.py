import os
from collections.abc import Callable
from typing import Annotated

from pydantic import BaseModel

from coyaml import YResource, coyaml
from coyaml._internal.node import YNode
from coyaml._internal.registry import YRegistry

# --- complex types support --------------------------------------------------


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


def test_basic_types(
    load_config: Callable[[str], None], function_with_basic_types: Callable[..., tuple[int, bool, str]]
) -> None:
    os.environ['DB_USER'] = 'test_user'
    os.environ['DB_PASSWORD'] = 'test_password'  # noqa: S105

    load_config('tests/config/config.yaml')
    result = function_with_basic_types()
    assert result == (9, True, 'path/to/llm/config')
    YRegistry.remove_config()


def test_pydantic_model(load_config: Callable[[str], None]) -> None:
    """Проверяем конвертацию в Pydantic-модель и работу YNode."""

    load_config('tests/config/config.yaml')

    db, db_node = function_with_complex_types()

    assert isinstance(db, DBConfig)  # noqa: S101
    assert isinstance(db_node, YNode)  # noqa: S101

    db1 = YRegistry.get_config().debug.db.to(DBConfig)
    assert db == db1  # noqa: S101

    YRegistry.remove_config()
