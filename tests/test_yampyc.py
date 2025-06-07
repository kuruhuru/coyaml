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
    """Debug configuration model containing database configuration."""

    db: DatabaseConfig


class AppConfig(BaseModel):
    """Main application configuration model containing debug and LLM parameters."""

    debug: DebugConfig
    llm: str


def test_loading_yaml_and_env_sources() -> None:
    """
    Test loading data from YAML and .env files.
    Checks the correctness of data retrieval from different sources.
    """
    config = Yampyc()
    config.add_yaml_source('tests/config/config.yaml')
    config.add_env_source('tests/config/config.env')

    # Set and get configuration from factory singleton
    YampycFactory.set_config(config)
    config = YampycFactory.get_config()

    # Check value from YAML
    assert config.index == 9, "Incorrect value 'index' from YAML file."

    # Check value from .env file
    assert config.ENV1 == '1.0', "Incorrect value 'ENV1' from .env file."
    assert config.get('ENV2') == 'String from env file', "Incorrect value 'ENV2' from .env file."


def test_converting_to_pydantic_model() -> None:
    """
    Test converting configuration data to Pydantic models.
    Verifies that configuration is correctly converted to a Pydantic model.
    """
    config = Yampyc()
    config.add_yaml_source('tests/config/config.yaml')

    # Convert to Pydantic model
    debug: DebugConfig = config.debug.to(DebugConfig)
    assert debug.db.url == 'postgres://user:password@localhost/dbname', 'Incorrect database URL.'

    # Check another model
    app_config: AppConfig = config.to(AppConfig)
    assert app_config.llm == 'path/to/llm/config', 'Incorrect LLM configuration.'


def test_assignment_operations() -> None:
    """
    Test assignment operations for new parameters in configuration.
    Verifies value assignment through attributes and dot notation.
    """
    config = Yampyc()
    config.add_yaml_source('tests/config/config.yaml')

    # Example of parameter value assignment
    config.index = 10
    assert config.index == 10, "Error assigning value to 'index'."

    # Assigning new parameters
    config.new_param = 'value'
    assert config.new_param == 'value', "Error assigning new parameter 'new_param'."

    # Example of working with dictionaries and lists
    config.new_param_dict = {'key': 'value'}
    assert config.new_param_dict == {'key': 'value'}, 'Error assigning dictionary.'

    config.new_param_list = [{'key1': 'value1'}, {'key2': 'value2'}]
    assert isinstance(config.new_param_list[0], YampycNode), 'Error assigning list of dictionaries.'
    assert config.new_param_list[0]['key1'] == 'value1', 'Error in list of dictionaries value.'


def test_dot_notation_access() -> None:
    """
    Test accessing configuration parameters using dot notation.
    Checks both reading and writing values.
    """
    config = Yampyc()
    config.add_yaml_source('tests/config/config.yaml')

    # Check reading through dot notation
    assert config['debug.db.url'] == 'postgres://user:password@localhost/dbname', 'Error reading through dot notation.'

    # Check writing through dot notation
    config['debug.db.url'] = 'sqlite:///yampyc.db'
    assert config['debug.db.url'] == 'sqlite:///yampyc.db', 'Error writing through dot notation.'


def test_invalid_key_access() -> None:
    """
    Test handling of invalid keys.
    Verifies that an exception is raised when accessing a non-existent key.
    """
    config = Yampyc()
    config.add_yaml_source('tests/config/config.yaml')

    try:
        config['non.existent.key']
    except KeyError:
        pass
    else:
        raise AssertionError('Expected KeyError when accessing non-existent key.')


def test_empty_config() -> None:
    """
    Test working with empty configuration.
    Verifies that empty configuration doesn't cause errors when reading and writing.
    """
    config = Yampyc()

    # Empty configuration should not have any keys
    try:
        config['any.key']
    except KeyError:
        pass
    else:
        raise AssertionError('Expected KeyError when accessing non-existent key in empty configuration.')

    # Can add new keys
    config['new.key'] = 'value'
    assert config['new.key'] == 'value', 'Error adding new key to empty configuration.'


def test_to_method_with_string() -> None:
    """
    Test to method with string path to class.
    Verifies correct dynamic class loading.
    """
    config = Yampyc()
    config.add_yaml_source('tests/config/config.yaml')

    # Use string path to load AppConfig class
    app_config: AppConfig = config.to('test_yampyc.AppConfig')
    assert isinstance(app_config, AppConfig), 'Error loading model through string.'
    assert app_config.llm == 'path/to/llm/config', 'Error converting configuration.'


def test_to_method_invalid_class() -> None:
    """
    Test to method with invalid class path.
    Expects ImportError.
    """
    config = Yampyc()

    with pytest.raises(ModuleNotFoundError):
        config.to('invalid.module.ClassName')


def test_to_method_invalid_attribute() -> None:
    """
    Test to method with invalid class name in existing module.
    Expects AttributeError.
    """
    config = Yampyc()

    with pytest.raises(ModuleNotFoundError):
        config.to('yampyc_test.InvalidClassName')
    with pytest.raises(AttributeError):
        config.to('test_yampyc.InvalidClassName')


def test_to_method_with_class() -> None:
    """
    Test to method with direct class passing.
    Verifies correct conversion of configuration to model object.
    """
    config = Yampyc()
    config.add_yaml_source('tests/config/config.yaml')

    app_config = config.to(AppConfig)
    assert isinstance(app_config, AppConfig), 'Error converting to model object.'
    assert app_config.llm == 'path/to/llm/config', 'Error in model data.'


def test_iteration_over_keys() -> None:
    """
    Test iteration over keys in YampycNode.
    """
    config = YampycNode({'key1': 'value1', 'key2': 'value2'})

    keys = list(config)
    assert keys == ['key1', 'key2'], 'Error in key iteration.'


def test_iteration_over_items() -> None:
    """
    Test iteration over keys and values in YampycNode.
    """
    config = YampycNode({'key1': 'value1', 'key2': 'value2'})

    items = list(config.items())
    assert items == [
        ('key1', 'value1'),
        ('key2', 'value2'),
    ], 'Error in key-value iteration.'


def test_iteration_over_values() -> None:
    """
    Test iteration over values in YampycNode.
    """
    config = YampycNode({'key1': 'value1', 'key2': 'value2'})

    values = list(config.values())
    assert values == ['value1', 'value2'], 'Error in value iteration.'


def test_parsing_env_vars_in_yaml_with_default() -> None:
    """
    Test for checking correct replacement of environment variables in YAML file with default value support.
    """
    # Set environment variables for test
    os.environ['DB_USER'] = 'test_user'

    # Important: DB_PASSWORD should not be set in environment
    if 'DB_PASSWORD' in os.environ:
        del os.environ['DB_PASSWORD']

    config = Yampyc()
    config.add_yaml_source('tests/config/config.yaml')
    config.resolve_templates()

    # Check that environment variables are correctly substituted
    assert config['debug.db.user'] == 'test_user', "Error in environment variable replacement for 'db.user'."
    assert config['debug.db.password'] == 'strong:/-password', "Error in using default value for 'db.password'."

    # Set DB_PASSWORD value and check again
    os.environ['DB_PASSWORD'] = 'real_password'  # noqa: S105

    config = Yampyc()
    config.add_yaml_source('tests/config/config.yaml')
    config.resolve_templates()

    assert config.debug.db.password == 'real_password', "Error in environment variable replacement for 'db.password'."  # noqa: S105


def test_missing_env_var_without_default() -> None:
    """
    Test for checking handling of situation when environment variable is not set and no default value is specified.
    """
    # Ensure environment variable is not set
    if 'DB_USER' in os.environ:
        del os.environ['DB_USER']

    config = Yampyc()

    with pytest.raises(  # noqa: PT012
        ValueError,
        match=r'Environment variable DB_USER is not set and has no default value.',
    ):
        config.add_yaml_source('tests/config/config.yaml')
        config.resolve_templates()


def test_template_parsing() -> None:
    """
    Test for checking correct processing of all template types in configuration.
    """
    # Set environment variables for test
    os.environ['DB_USER'] = 'test_user'
    os.environ['DB_PASSWORD'] = 'test_password'  # noqa: S105

    config = Yampyc()
    config.add_yaml_source('tests/config/config.yaml')
    config.resolve_templates()

    # Check environment variable replacement
    assert config['debug.db.user'] == 'test_user', "Error in environment variable replacement for 'debug.db.user'."
    assert (
        config['debug.db.password'] == 'test_password'
    ), "Error in environment variable replacement for 'debug.db.password'."

    # Check file content insertion
    with open('tests/config/init.sql') as f:
        init_script_content = f.read()
    assert config['debug.db.init_script'] == init_script_content, "Error in file content insertion for 'init.sql'."

    # Check value insertion from current configuration
    expected_db_url = f'postgresql://{config["debug.db.user"]}:{config["debug.db.password"]}@localhost:5432/app_db'
    assert (
        config['app.db_url'] == expected_db_url
    ), "Error in value insertion from current configuration in 'app.db_url'."

    # Check external YAML file loading
    assert (
        config['app.extra_settings.feature_flags.enable_new_feature'] is True
    ), "Error in external YAML file loading and reading 'enable_new_feature'."
    assert (
        config['app.extra_settings.feature_flags.beta_mode'] is False
    ), "Error in external YAML file loading and reading 'beta_mode'."


def test_file_not_found() -> None:
    """
    Test for checking handling of situation when file for insertion is not found.
    """
    # Change file path to non-existent
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
    """
    Test for checking handling of situation when external YAML file is not found.
    """
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
    """
    Test for checking handling of situation when unknown action is specified in template.
    """
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
        match=r'Unknown action in template: unknown_action',
    ):
        config.resolve_templates()

    # Remove temporary file
    os.remove('tests/config/temp_config.yaml')


def test_recursive_template_resolution() -> None:
    """
    Test for checking recursive template processing.
    """
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

    assert config['app.final_value'] == 'resolved_value', 'Error in recursive template processing.'

    # Remove temporary file and environment variables
    os.remove('tests/config/temp_config.yaml')
    del os.environ['NESTED_ENV']
    del os.environ['FINAL_ENV']


def test_config_key_not_found() -> None:
    """
    Test for checking handling of situation when key is not found in configuration when using config template.
    """
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
        match=r"Key 'nonexistent.key' not found in configuration.",
    ):
        config.resolve_templates()

    # Remove temporary file
    os.remove('tests/config/temp_config.yaml')


# Run tests
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
