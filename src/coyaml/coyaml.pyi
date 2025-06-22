# coyaml.pyi
from collections.abc import Callable
from typing import TypeVar

from typing_extensions import ParamSpec

P = ParamSpec('P')
R = TypeVar('R')

def coyaml(func: Callable[P, R]) -> Callable[..., R]: ...
