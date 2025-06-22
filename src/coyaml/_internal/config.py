# src/coyaml/_internal/config.py

import os
import re
from typing import Any

import yaml

from coyaml._internal.node import YNode
from coyaml.sources.base import YSource
from coyaml.utils.merge import deep_merge

# Pattern for finding variable names
TEMPLATE_PATTERN = re.compile(r'\${{\s*(\w+):(.+?)}}')


class YSettings(YNode):
    """
    Основной контейнер настроек.
    Хранит агрегированные данные из нескольких источников (:class:`YSource`).
    Наследуется от :class:`YNode`, поэтому поддерживает точечную нотацию и метод ``to``.
    """

    def __init__(self, initial: dict[str, Any] | None = None):
        super().__init__(initial or {})
        self._sources: list[YSource] = []

    def add_source(self, source: YSource) -> 'YSettings':
        """Загрузить данные из источника и слить в текущий объект."""
        data = source.load()
        deep_merge(self._data, data)
        self._sources.append(source)
        return self

    def resolve_templates(self) -> None:
        """
        Recursively traverse configuration data and process all templates.

        This method performs a second pass through the previously loaded configuration, replacing all
        templates in the format `${{ action:parameters }}` with corresponding values. The following
        actions are supported:

        - **env**: Insert environment variable value.
        Syntax: `${{ env:VARIABLE_NAME[:DEFAULT_VALUE] }}`.
        If environment variable `VARIABLE_NAME` is not set and default value
        `DEFAULT_VALUE` is not specified, a `ValueError` is raised.

        - **file**: Insert text file content.
        Syntax: `${{ file:PATH_TO_FILE }}`.
        If file at path `PATH_TO_FILE` is not found, a `FileNotFoundError` is raised.

        - **config**: Insert value from current configuration.
        Syntax: `${{ config:PATH.TO.NODE }}`.
        If specified path `PATH.TO.NODE` is not found in configuration, a `KeyError` is raised.

        - **yaml**: Load and insert external YAML file.
        Syntax: `${{ yaml:PATH_TO_YAML_FILE }}`.
        If file at path `PATH_TO_YAML_FILE` is not found, a `FileNotFoundError` is raised.

        The method processes templates in string values of the configuration. If the replacement result
        is also a string containing templates, processing is repeated recursively until all templates
        are fully resolved.

        Example usage:

        ```yaml
        database:
            user: ${{ env:DB_USER }}
            password: ${{ env:DB_PASSWORD:default_password }}
            init_script: ${{ file:./scripts/init.sql }}
        app:
            db_url: "postgresql://${{ config:database.user }}:${{ config:database.password }}@localhost:5432/app_db"
            extra_settings: ${{ yaml:./configs/extra.yaml }}
        ```

        After calling `resolve_templates()`, all templates in the configuration will be replaced with real values.

        :raises ValueError:
            - If unknown action is specified in template.
            - If environment variable is not set and has no default value.
            - If `config` template inside string returns value of type `dict` or `list`.
            - If trying to use `yaml` template inside string.

        :raises KeyError:
            - If specified key is not found in configuration when using `config` action.

        :raises FileNotFoundError:
            - If file is not found when using `file` or `yaml` actions.

        :return: None. Method modifies object state by updating configuration data.
        """
        self._data = self._resolve_node(self._data)

    def _resolve_node(self, node: Any) -> Any:
        if isinstance(node, dict):
            return {k: self._resolve_node(v) for k, v in node.items()}
        elif isinstance(node, list):
            return [self._resolve_node(v) for v in node]
        elif isinstance(node, str):
            new_value = self._resolve_value(node)
            while isinstance(new_value, str) and new_value != node:
                node = new_value
                new_value = self._resolve_value(node)
            return new_value
        else:
            return node

    def _resolve_value(self, value: str) -> Any:
        match = TEMPLATE_PATTERN.fullmatch(value.strip())
        if match:
            action = match.group(1)
            params = match.group(2)
            if action == 'env':
                return self._handle_env(params)
            elif action == 'file':
                return self._handle_file(params)
            elif action == 'config':
                return self._handle_config(params)
            elif action == 'yaml':
                return self._handle_yaml(params)
            else:
                raise ValueError(f'Unknown action in template: {action}')
        else:
            # Replace any embedded templates within the string
            def replace_match(match: re.Match[str]) -> str:
                action = match.group(1)
                params = match.group(2)
                if action == 'env':
                    return self._handle_env(params)
                elif action == 'file':
                    return self._handle_file(params)
                elif action == 'config':
                    value = self._handle_config(params)
                    if isinstance(value, dict | list):
                        raise ValueError('Config template cannot return dict or list inside string.')
                    return str(value)
                elif action == 'yaml':
                    raise ValueError('YAML template cannot be used inside string.')
                else:
                    raise ValueError(f'Unknown action in template: {action}')

            return TEMPLATE_PATTERN.sub(replace_match, value)

    # Implementation of handling methods for each action
    def _handle_env(self, params: str) -> str:
        # Split only by first colon
        if ':' in params:
            var_name, default_value = params.split(':', 1)
            var_name = var_name.strip()
            default_value = default_value.strip()
        else:
            var_name = params.strip()
            default_value = None

        value = os.getenv(var_name, default_value)
        if value is None:
            raise ValueError(f'Environment variable {var_name} is not set and has no default value.')
        return value

    def _handle_file(self, params: str) -> str:
        file_path = params.strip()
        try:
            with open(file_path, 'rb') as f:  # Changed to binary mode
                binary_content = f.read()
                try:
                    return binary_content.decode('utf-8')
                except UnicodeDecodeError as e:
                    raise UnicodeDecodeError(
                        'utf-8',  # encoding
                        binary_content,  # object
                        e.start,  # start
                        e.end,  # end
                        f'Error decoding file {file_path}: {e}',
                    ) from e
        except FileNotFoundError as e:
            raise FileNotFoundError(f'File not found: {file_path}') from e

    def _handle_config(self, params: str) -> Any:
        config_path = params.strip()
        keys = config_path.split('.')
        value = self._data
        for key in keys:
            if key not in value:
                raise KeyError(f"Key '{config_path}' not found in configuration.")
            value = value[key]
        return value

    def _handle_yaml(self, params: str) -> Any:
        file_path = params.strip()
        try:
            with open(file_path, 'rb') as f:  # Changed to binary mode
                binary_content = f.read()
                try:
                    text_content = binary_content.decode('utf-8')
                except UnicodeDecodeError as e:
                    raise UnicodeDecodeError(
                        'utf-8',  # encoding
                        binary_content,  # object
                        e.start,  # start
                        e.end,  # end
                        f'Error decoding file {file_path}: {e}',
                    ) from e
                yaml_content = yaml.safe_load(text_content)
                # After loading external YAML file, we need to process its templates as well
                return self._resolve_node(yaml_content)
        except FileNotFoundError as e:
            raise FileNotFoundError(f'YAML file not found: {file_path}') from e
