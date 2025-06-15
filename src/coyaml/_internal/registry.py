# src/coyaml/_internal/factory.py

import threading
from typing import Any

from coyaml._internal.config import YConfig
from coyaml._internal.deps import YDeps
from coyaml.sources.base import YSource


class YRegistry:
    """
    Registry and factory for named YConfig instances.
    If a key is provided, the config is stored in the registry.
    If no key is provided, the 'default' key is used.
    Supports creating configs from URI schemes and lists of URIs.
    """

    _instances: dict[str, YConfig] = {}
    _lock = threading.Lock()
    _scheme_map: dict[str, Any] = {}  # scheme -> YSource subclass or factory func
    _deps: YDeps | None = None

    @classmethod
    def register_scheme(cls, scheme: str, handler: Any) -> None:
        """
        Register a URI scheme for config creation.

        Args:
            scheme: URI scheme name (e.g., 'yaml', 'env', 'redis').
            handler: YSource subclass or factory function accepting (uri, **kwargs).
        """
        cls._scheme_map[scheme] = handler

    @classmethod
    def set_config(cls, config: YConfig, key: str = 'default') -> None:
        """
        Store a YConfig instance under the given key.

        Args:
            config: YConfig instance to store.
            key: Key under which to store the config.
        """
        with cls._lock:
            cls._instances[key] = config

    @classmethod
    def get_config(cls, key: str = 'default') -> YConfig:
        """
        Retrieve a stored config by key.

        Raises:
            KeyError if config not found.
        """
        with cls._lock:
            if key not in cls._instances:
                raise KeyError(f"Config '{key}' not found")
            return cls._instances[key]

    @classmethod
    def set_deps(cls, deps: YDeps) -> None:
        """Store a YDeps container for dependency providers."""
        cls._deps = deps

    @classmethod
    def get_deps(cls) -> YDeps:
        """Retrieve stored YDeps container."""
        if cls._deps is None:
            raise KeyError('Dependencies container not set')
        return cls._deps

    @classmethod
    def create_from_uri_list(
        cls, uri_list: list[str], key: str | None = None, resolve_templates: bool = True, **kwargs: Any
    ) -> YConfig:
        """
        Create a YConfig by parsing a list of URIs and loading the corresponding sources.
        The sources are added to the config in the order they are provided.
        The last source takes precedence over the previous ones.

        Args:
            uri_list: List of URIs to load.
            key: Optional name under which to store the config.
            resolve_templates: Whether to resolve templates in the sources.
            kwargs: Additional params passed to source handler.

        Returns:
            The created YConfig.
        """
        config = YConfig()
        for uri in uri_list:
            scheme, path = uri.split('://', 1)
            if scheme not in cls._scheme_map:
                raise ValueError(f"Unknown config scheme '{scheme}'")
            source_ctor = cls._scheme_map[scheme]
            # Instantiate source (either class or factory function)
            source: YSource = source_ctor(path, **kwargs) if callable(source_ctor) else source_ctor(path, **kwargs)
            config = YConfig().add_source(source)
        # Optionally resolve templates here
        if resolve_templates:
            config.resolve_templates()
        if key:
            cls.set_config(config=config, key=key)
        return config

    @classmethod
    def create_from_uri(
        cls, uri: str, key: str | None = None, resolve_templates: bool = True, **kwargs: Any
    ) -> YConfig:
        """
        Create a YConfig by parsing a URI and loading the corresponding source.

        Args:
            uri: e.g. "yaml://path/to/config.yaml" or "env://./.env"
            key: Optional name under which to store the config.
            kwargs: Additional params passed to source handler.

        Returns:
            The created YConfig.
        """
        return cls.create_from_uri_list([uri], key, resolve_templates, **kwargs)
