# tests/test_yampyc.py
import os

import pytest
from pydantic import BaseModel

from yampyc import (
    Yampyc,
    YampycFactory,
    YampycNode,
)


class DatabaseConfig(BaseModel):
    """Database configuration model."""

    url: str


class DebugConfig(BaseModel):
    """Debug configuration model containing database settings."""

    db: DatabaseConfig


class AppConfig(BaseModel):
    """Main application configuration model with debug and LLM parameters."""

    debug: DebugConfig
    llm: str


def test_loading_yaml_and_env_sources() -> None:
    """Test loading data from YAML and .env files.

    Ensures data from different sources is read correctly.
    """
    config = Yampyc()
    config.add_yaml_source('tests/config/config.yaml')
    config.add_env_source('tests/config/config.env')

    # Установка и получение конфигурации из фабрики синглтонов
    YampycFactory.set_config(config)
    config = YampycFactory.get_config()

    # Проверка значения из YAML
    assert config.index == 9, "Неверное значение 'index' из YAML файла."

    # Проверка значения из .env файла
    assert config.ENV1 == '1.0', "Неверное значение 'ENV1' из .env файла."
    assert config.get('ENV2') == 'String from env file', "Неверное значение 'ENV2' из .env файла."


def test_converting_to_pydantic_model() -> None:
    """Test converting configuration data to Pydantic models."""
    config = Yampyc()
    config.add_yaml_source('tests/config/config.yaml')

    # Convert to a Pydantic model
    debug: DebugConfig = config.debug.to(DebugConfig)
    assert debug.db.url == 'postgres://user:password@localhost/dbname', 'Invalid database URL.'

    # Check conversion to another model
    app_config: AppConfig = config.to(AppConfig)
    assert app_config.llm == 'path/to/llm/config', 'Incorrect LLM configuration.'


def test_assignment_operations() -> None:
    """Test assigning new parameters via attributes and dot notation."""
    config = Yampyc()
    config.add_yaml_source('tests/config/config.yaml')

    # Example of assigning a parameter value
    config.index = 10
    assert config.index == 10, "Failed to assign value to 'index'."

    # Assigning new parameters
    config.new_param = 'value'
    assert config.new_param == 'value', "Failed to assign new parameter 'new_param'."

    # Example working with dictionaries and lists
    config.new_param_dict = {'key': 'value'}
    assert config.new_param_dict == {'key': 'value'}, 'Failed to assign dictionary.'

    config.new_param_list = [{'key1': 'value1'}, {'key2': 'value2'}]
    assert isinstance(config.new_param_list[0], YampycNode), 'Failed to assign list of dictionaries.'
    assert config.new_param_list[0]['key1'] == 'value1', 'Incorrect value in list of dictionaries.'


def test_dot_notation_access() -> None:
    """Test accessing configuration parameters via dot notation."""
    config = Yampyc()
    config.add_yaml_source('tests/config/config.yaml')

    # Check reading via dot notation
    assert (
        config['debug.db.url'] == 'postgres://user:password@localhost/dbname'
    ), 'Failed reading via dot notation.'

    # Check writing via dot notation
    config['debug.db.url'] = 'sqlite:///yampyc.db'
    assert config['debug.db.url'] == 'sqlite:///yampyc.db', 'Failed writing via dot notation.'


def test_invalid_key_access() -> None:
    """Ensure a ``KeyError`` is raised for invalid keys."""
    config = Yampyc()
    config.add_yaml_source('tests/config/config.yaml')

    try:
        config['non.existent.key']
    except KeyError:
        pass
    else:
        raise AssertionError('Expected KeyError when accessing a non-existent key.')


def test_empty_config() -> None:
    """Check that an empty configuration can be read and written."""
    config = Yampyc()

    # An empty configuration should have no keys
    try:
        config['any.key']
    except KeyError:
        pass
    else:
        raise AssertionError('Expected KeyError when accessing a missing key in an empty configuration.')

    # New keys can be added
    config['new.key'] = 'value'
    assert config['new.key'] == 'value', 'Failed to add new key to empty configuration.'


def test_to_method_with_string() -> None:
    """Test ``to`` method using a dotted path to the class."""
    config = Yampyc()
    config.add_yaml_source('tests/config/config.yaml')

    # Use a dotted path to load ``AppConfig``
    app_config: AppConfig = config.to('test_yampyc.AppConfig')
    assert isinstance(app_config, AppConfig), 'Failed to load model from string.'
    assert app_config.llm == 'path/to/llm/config', 'Configuration conversion error.'


def test_to_method_invalid_class() -> None:
    """Expect ``ImportError`` when a module path is invalid."""
    config = Yampyc()

    with pytest.raises(ModuleNotFoundError):
        config.to('invalid.module.ClassName')


def test_to_method_invalid_attribute() -> None:
    """Expect ``AttributeError`` when class name is invalid."""
    config = Yampyc()

    with pytest.raises(ModuleNotFoundError):
        config.to('yampyc_test.InvalidClassName')
    with pytest.raises(AttributeError):
        config.to('test_yampyc.InvalidClassName')


def test_to_method_with_class() -> None:
    """Test ``to`` method when a class is passed directly."""
    config = Yampyc()
    config.add_yaml_source('tests/config/config.yaml')

    app_config = config.to(AppConfig)
    assert isinstance(app_config, AppConfig), 'Failed to convert to model instance.'
    assert app_config.llm == 'path/to/llm/config', 'Model data error.'


def test_iteration_over_keys() -> None:
    """Test iteration over keys in ``YampycNode``."""
    config = YampycNode({'key1': 'value1', 'key2': 'value2'})

    keys = list(config)
    assert keys == ['key1', 'key2'], 'Iteration over keys failed.'


def test_iteration_over_items() -> None:
    """Test iteration over key/value pairs in ``YampycNode``."""
    config = YampycNode({'key1': 'value1', 'key2': 'value2'})

    items = list(config.items())
    assert items == [
        ('key1', 'value1'),
        ('key2', 'value2'),
    ], 'Iteration over items failed.'


def test_iteration_over_values() -> None:
    """Test iteration over values in ``YampycNode``."""
    config = YampycNode({'key1': 'value1', 'key2': 'value2'})

    values = list(config.values())
    assert values == ['value1', 'value2'], 'Iteration over values failed.'


def test_parsing_env_vars_in_yaml_with_default() -> None:
    """Check substitution of environment variables in YAML with defaults."""
    # Set environment variables for the test
    os.environ['DB_USER'] = 'test_user'

    # Ensure DB_PASSWORD is not set
    if 'DB_PASSWORD' in os.environ:
        del os.environ['DB_PASSWORD']

    config = Yampyc()
    config.add_yaml_source('tests/config/config.yaml')
    config.resolve_templates()

    # Verify environment variables were substituted correctly
    assert config['debug.db.user'] == 'test_user', "Environment variable substitution failed for 'db.user'."
    assert (
        config['debug.db.password'] == 'strong:/-password'
    ), "Default value for 'db.password' was not used correctly."

    # Set DB_PASSWORD and check again
    os.environ['DB_PASSWORD'] = 'real_password'  # noqa: S105

    config = Yampyc()
    config.add_yaml_source('tests/config/config.yaml')
    config.resolve_templates()

    assert config.debug.db.password == 'real_password', "Environment variable substitution failed for 'db.password'."  # noqa: S105


def test_missing_env_var_without_default() -> None:
    """Check behaviour when an environment variable is missing and no default is given."""
    # Ensure the environment variable is not set
    if 'DB_USER' in os.environ:
        del os.environ['DB_USER']

    config = Yampyc()

    with pytest.raises(  # noqa: PT012
        ValueError,
        match=r'Переменная окружения DB_USER не задана и не имеет значения по умолчанию.',
    ):
        config.add_yaml_source('tests/config/config.yaml')
        config.resolve_templates()


def test_template_parsing() -> None:
    """Test processing of all template types in the configuration."""
    # Set environment variables for the test
    os.environ['DB_USER'] = 'test_user'
    os.environ['DB_PASSWORD'] = 'test_password'  # noqa: S105

    config = Yampyc()
    config.add_yaml_source('tests/config/config.yaml')
    config.resolve_templates()

    # Check that environment variables were replaced
    assert config['debug.db.user'] == 'test_user', "Environment variable substitution failed for 'debug.db.user'."
    assert (
        config['debug.db.password'] == 'test_password'
    ), "Environment variable substitution failed for 'debug.db.password'."

    # Check file content insertion
    with open('tests/config/init.sql') as f:
        init_script_content = f.read()
    assert config['debug.db.init_script'] == init_script_content, "File content insertion failed for 'init.sql'."

    # Check insertion of a value from current configuration
    expected_db_url = f'postgresql://{config["debug.db.user"]}:{config["debug.db.password"]}@localhost:5432/app_db'
    assert config['app.db_url'] == expected_db_url, "Failed to insert value from current configuration into 'app.db_url'."

    # Check loading of an external YAML file
    assert (
        config['app.extra_settings.feature_flags.enable_new_feature'] is True
    ), "Failed to load external YAML file or read 'enable_new_feature'."
    assert (
        config['app.extra_settings.feature_flags.beta_mode'] is False
    ), "Failed to load external YAML file or read 'beta_mode'."


def test_file_not_found() -> None:
    """Check handling when an included file is missing."""
    # Use a nonexistent path
    config_content = """
    debug:
      db:
        init_script: ${{ file:./scripts/nonexistent.sql }}
    """
    with open('tests/config/temp_config.yaml', 'w') as f:
        f.write(config_content)

    config = Yampyc()
    config.add_yaml_source('tests/config/temp_config.yaml')

    with pytest.raises(
        FileNotFoundError,
    ):
        config.resolve_templates()

    # Remove temporary file
    os.remove('tests/config/temp_config.yaml')


def test_yaml_file_not_found() -> None:
    """Check handling when an external YAML file is missing."""
    config_content = """
    app:
      extra_settings: ${{ yaml:./configs/nonexistent.yaml }}
    """
    with open('tests/config/temp_config.yaml', 'w') as f:
        f.write(config_content)

    config = Yampyc()
    config.add_yaml_source('tests/config/temp_config.yaml')

    with pytest.raises(
        FileNotFoundError,
    ):
        config.resolve_templates()

    # Remove temporary file
    os.remove('tests/config/temp_config.yaml')


def test_invalid_template_action() -> None:
    """Check handling of an unknown template action."""
    config_content = """
    app:
      invalid_template: ${{ unknown_action:some_value }}
    """
    with open('tests/config/temp_config.yaml', 'w') as f:
        f.write(config_content)

    config = Yampyc()
    config.add_yaml_source('tests/config/temp_config.yaml')

    with pytest.raises(
        ValueError,
        match=r'Неизвестное действие в шаблоне: unknown_action',
    ):
        config.resolve_templates()

    # Remove temporary file
    os.remove('tests/config/temp_config.yaml')


def test_recursive_template_resolution() -> None:
    """Test recursive template processing."""
    config_content = """
    app:
      nested_value: ${{ env:NESTED_ENV }}
      final_value: ${{ config:app.nested_value }}
    """
    os.environ['NESTED_ENV'] = '${{ env:FINAL_ENV }}'
    os.environ['FINAL_ENV'] = 'resolved_value'

    with open('tests/config/temp_config.yaml', 'w') as f:
        f.write(config_content)

    config = Yampyc()
    config.add_yaml_source('tests/config/temp_config.yaml')
    config.resolve_templates()

    assert config['app.final_value'] == 'resolved_value', 'Recursive template resolution failed.'

    # Clean up temporary file and environment variables
    os.remove('tests/config/temp_config.yaml')
    del os.environ['NESTED_ENV']
    del os.environ['FINAL_ENV']


def test_config_key_not_found() -> None:
    """Check behaviour when a config key is missing for ``config`` template."""
    config_content = """
    app:
      missing_value: ${{ config:nonexistent.key }}
    """
    with open('tests/config/temp_config.yaml', 'w') as f:
        f.write(config_content)

    config = Yampyc()
    config.add_yaml_source('tests/config/temp_config.yaml')

    with pytest.raises(
        KeyError,
        match=r"Key 'nonexistent.key' not found in the configuration",
    ):
        config.resolve_templates()

    # Remove temporary file
    os.remove('tests/config/temp_config.yaml')


# Запуск тестов
if __name__ == '__main__':
    test_loading_yaml_and_env_sources()
    test_converting_to_pydantic_model()
    test_assignment_operations()
    test_dot_notation_access()
    test_invalid_key_access()
    test_empty_config()
    test_to_method_with_string()
    test_to_method_invalid_class()
    test_to_method_invalid_attribute()
    test_to_method_with_class()
    test_iteration_over_keys()
    test_iteration_over_items()
    test_iteration_over_values()
    test_parsing_env_vars_in_yaml_with_default()
    test_missing_env_var_without_default()
    test_template_parsing()
    test_file_not_found()
    test_yaml_file_not_found()
    test_invalid_template_action()
    test_recursive_template_resolution()
    test_config_key_not_found()
