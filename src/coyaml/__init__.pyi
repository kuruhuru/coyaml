from collections.abc import Callable
from typing import ParamSpec, TypeVar, overload

# Re-exports for type checkers
from coyaml._internal._config import YConfig as YConfig
from coyaml._internal._config import YConfigFactory as YConfigFactory
from coyaml._internal.config import YSettings as YSettings
from coyaml._internal.node import YNode as YNode
from coyaml._internal.registry import YRegistry as YRegistry
from coyaml.sources.base import YSource as YSource
from coyaml.sources.env import EnvFileSource as EnvFileSource
from coyaml.sources.yaml import YamlFileSource as YamlFileSource
from coyaml.utils.merge import deep_merge as deep_merge

P = ParamSpec('P')
R = TypeVar('R')

@overload
def coyaml(func: Callable[P, R]) -> Callable[..., R]: ...
@overload
def coyaml(
    *, mask: str | list[str] | None = ..., unique: bool = ...
) -> Callable[[Callable[P, R]], Callable[..., R]]: ...

class YResource:
    def __init__(self, path: str | None = ..., config: str = ...) -> None: ...
