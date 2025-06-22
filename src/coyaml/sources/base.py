# src/coyaml/sources/base.py

from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Any


class YSource(ABC):
    """Abstract base class for configuration sources."""

    @abstractmethod
    def load(self) -> dict[str, Any]:
        """
        Load configuration data from this source.

        Returns:
            A dict representing configuration values.
        """
        ...

    def watch(self, callback: Callable[[], None]) -> None:
        """
        Optional: watch this source for changes and invoke callback.
        Subclasses may override to implement file-watch, pub/sub, etc.
        """
        # no-op by default
        raise NotImplementedError('watch is not implemented')
