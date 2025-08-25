from collections.abc import Callable
from typing import ParamSpec, TypeVar, overload

P = ParamSpec('P')
R = TypeVar('R')

@overload
def coyaml(func: Callable[P, R]) -> Callable[P, R]: ...
@overload
def coyaml(*, mask: str | list[str] | None = ..., unique: bool = ...) -> Callable[[Callable[P, R]], Callable[P, R]]: ...

class YResource:
    def __init__(self, path: str | None = ..., config: str = ...) -> None: ...
