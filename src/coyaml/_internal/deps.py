# src/coyaml/_internal/deps.py

from collections.abc import Callable
from typing import Any


class YDeps:
    """
    Container for dependency providers, to be used for
    future injection mechanisms.
    """

    def __init__(self) -> None:
        self._providers: dict[str, Callable[[], Any]] = {}

    def register(self, name: str, provider: Callable[[], Any]) -> None:
        """
        Register a provider callable under a given name.

        Args:
            name: Identifier for the dependency.
            provider: Callable returning the dependency.
        """
        self._providers[name] = provider

    def get(self, name: str) -> Any:
        """
        Retrieve and invoke the provider for the given name.

        Args:
            name: Identifier of the dependency.

        Returns:
            The provided dependency.

        Raises:
            KeyError: If no provider is registered under `name`.
        """
        if name not in self._providers:
            raise KeyError(f"Dependency '{name}' not found")
        return self._providers[name]()
