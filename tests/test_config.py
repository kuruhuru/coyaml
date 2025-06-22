# tests/test_config.py
import os
from pathlib import Path

import pytest
from pydantic import BaseModel

from coyaml import (
    YNode,
    YRegistry,
)
from coyaml import (
    YSettings as YConfig,
)
from coyaml.sources.env import EnvFileSource
from coyaml.sources.yaml import YamlFileSource


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
    config = YConfig()
    config.add_source(YamlFileSource('tests/config/config.yaml'))
    config.add_source(EnvFileSource('tests/config/config.env'))

    # Set and get configuration from factory singleton
    YRegistry.set_config(config=config)
    config = YRegistry.get_config()

    # Check value from YAML
    assert config.index == 9, "Incorrect value 'index' from YAML file."

    # Check value from .env file
    assert config.ENV1 == '1.0', "Incorrect value 'ENV1' from .env file."
    assert config['ENV2'] == 'String from env file', "Incorrect value 'ENV2' from .env file."


def test_converting_to_pydantic_model() -> None:
    """
    Test converting configuration data to Pydantic models.
    Verifies that configuration is correctly converted to a Pydantic model.
    """
    config = YConfig()
    config.add_source(YamlFileSource('tests/config/config.yaml'))

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
    config = YConfig()
    config.add_source(YamlFileSource('tests/config/config.yaml'))

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
    assert isinstance(config.new_param_list[0], YNode), 'Error assigning list of dictionaries.'
    assert config.new_param_list[0]['key1'] == 'value1', 'Error in list of dictionaries value.'


def test_dot_notation_access() -> None:
    """
    Test accessing configuration parameters using dot notation.
    Checks both reading and writing values.
    """
    config = YConfig()
    config.add_source(YamlFileSource('tests/config/config.yaml'))

    # Check reading through dot notation
    assert config['debug.db.url'] == 'postgres://user:password@localhost/dbname', 'Error reading through dot notation.'

    # Check writing through dot notation
    config['debug.db.url'] = 'sqlite:///coyaml.db'
    assert config['debug.db.url'] == 'sqlite:///coyaml.db', 'Error writing through dot notation.'


def test_invalid_key_access() -> None:
    """
    Test handling of invalid keys.
    Verifies that an exception is raised when accessing a non-existent key.
    """
    config = YConfig()
    config.add_source(YamlFileSource('tests/config/config.yaml'))

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
    config = YConfig()

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
    config = YConfig()
    config.add_source(YamlFileSource('tests/config/config.yaml'))

    # Use string path to load AppConfig class
    app_config: AppConfig = config.to('test_config.AppConfig')
    assert isinstance(app_config, AppConfig), 'Error loading model through string.'
    assert app_config.llm == 'path/to/llm/config', 'Error converting configuration.'


def test_to_method_invalid_class() -> None:
    """
    Test to method with invalid class path.
    Expects ImportError.
    """
    config = YConfig()

    with pytest.raises(ModuleNotFoundError):
        config.to('invalid.module.ClassName')


def test_to_method_invalid_attribute() -> None:
    """
    Test to method with invalid class name in existing module.
    Expects AttributeError.
    """
    config = YConfig()

    with pytest.raises(ModuleNotFoundError):
        config.to('invalid_module.InvalidClassName')
    with pytest.raises(AttributeError):
        config.to('test_config.InvalidClassName')


def test_to_method_with_class() -> None:
    """
    Test to method with direct class passing.
    Verifies correct conversion of configuration to model object.
    """
    config = YConfig()
    config.add_source(YamlFileSource('tests/config/config.yaml'))

    app_config = config.to(AppConfig)
    assert isinstance(app_config, AppConfig), 'Error converting to model object.'
    assert app_config.llm == 'path/to/llm/config', 'Error in model data.'


def test_iteration_over_keys() -> None:
    """
    Test iteration over keys in YNode.
    """
    config = YNode({'key1': 'value1', 'key2': 'value2'})

    keys = list(config)
    assert keys == ['key1', 'key2'], 'Error in key iteration.'


def test_iteration_over_items() -> None:
    """
    Test iteration over keys and values in YNode.
    """
    config = YNode({'key1': 'value1', 'key2': 'value2'})

    items = list(config.items())
    assert items == [
        ('key1', 'value1'),
        ('key2', 'value2'),
    ], 'Error in key-value iteration.'


def test_iteration_over_values() -> None:
    """
    Test iteration over values in YNode.
    """
    config = YNode({'key1': 'value1', 'key2': 'value2'})

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

    config = YConfig()
    config.add_source(YamlFileSource('tests/config/config.yaml'))
    config.resolve_templates()

    # Check that environment variables are correctly substituted
    assert config['debug.db.user'] == 'test_user', "Error in environment variable replacement for 'db.user'."
    assert config['debug.db.password'] == 'strong:/-password', "Error in using default value for 'db.password'."

    # Set DB_PASSWORD value and check again
    os.environ['DB_PASSWORD'] = 'real_password'  # noqa: S105

    config = YConfig()
    config.add_source(YamlFileSource('tests/config/config.yaml'))
    config.resolve_templates()

    assert config.debug.db.password == 'real_password', "Error in environment variable replacement for 'db.password'."  # noqa: S105


def test_missing_env_var_without_default() -> None:
    """
    Test for checking handling of situation when environment variable is not set and no default value is specified.
    """
    # Ensure environment variable is not set
    if 'DB_USER' in os.environ:
        del os.environ['DB_USER']

    config = YConfig()

    with pytest.raises(  # noqa: PT012
        ValueError,
        match=r'Environment variable DB_USER is not set and has no default value.',
    ):
        config.add_source(YamlFileSource('tests/config/config.yaml'))
        config.resolve_templates()


def test_template_parsing() -> None:
    """
    Test for checking correct processing of all template types in configuration.
    """
    # Set environment variables for test
    os.environ['DB_USER'] = 'test_user'
    os.environ['DB_PASSWORD'] = 'test_password'  # noqa: S105

    config = YConfig()
    config.add_source(YamlFileSource('tests/config/config.yaml'))
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

    config = YConfig()
    config.add_source(YamlFileSource('tests/config/temp_config.yaml'))

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

    config = YConfig()
    config.add_source(YamlFileSource('tests/config/temp_config.yaml'))

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

    config = YConfig()
    config.add_source(YamlFileSource('tests/config/temp_config.yaml'))

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

    config = YConfig()
    config.add_source(YamlFileSource('tests/config/temp_config.yaml'))
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

    config = YConfig()
    config.add_source(YamlFileSource('tests/config/temp_config.yaml'))

    with pytest.raises(
        KeyError,
        match=r"Key 'nonexistent.key' not found in configuration.",
    ):
        config.resolve_templates()

    # Remove temporary file
    os.remove('tests/config/temp_config.yaml')


def test_to_dict() -> None:
    """Test converting YNode to dictionary."""
    data = {'key': 'value'}
    node = YNode(data)
    assert node.to_dict() == data


def test_eq_with_incompatible_types() -> None:
    """Test comparison with incompatible types."""
    node = YNode({'key': 'value'})
    assert not (node == 42)  # Compare with number
    assert not (node == 'string')  # Compare with string


def test_yaml_unicode_decode_error() -> None:
    """Test handling of UnicodeDecodeError when reading YAML file."""
    # Create temporary file with invalid encoding
    with open('tests/config/invalid.yaml', 'wb') as f:
        f.write(b'\xff\xfe')  # Invalid UTF-8 sequence

    config = YConfig()
    with pytest.raises(UnicodeDecodeError):
        config.add_source(YamlFileSource('tests/config/invalid.yaml'))

    # Remove temporary file
    os.remove('tests/config/invalid.yaml')


def test_nested_templates_in_strings() -> None:
    """Test handling of nested templates in strings."""
    os.environ['NESTED_VAR'] = 'nested_value'
    config = YConfig({'template': 'prefix ${{ env:NESTED_VAR }} suffix'})
    config.resolve_templates()
    assert config['template'] == 'prefix nested_value suffix'

    # Clean up environment variable
    del os.environ['NESTED_VAR']


def test_template_errors() -> None:
    """Test handling of various template errors."""
    config = YConfig()

    # Unknowniaction
    config['invalid'] = '${{ unknown:value }}'
    with pytest.raises(ValueError, match='Unknown action in template: unknown'):
        config.resolve_templates()

    # Config returns dict inside string
    config = YConfig({'dict': {'key': 'value'}})
    config['invalid'] = 'prefix ${{ config:dict }} suffix'
    with pytest.raises(ValueError, match='Config template cannot return dict or list inside string'):
        config.resolve_templates()


def test_config_factory_multiple_instances() -> None:
    """Test YConfigFactory with multiple instances."""
    config1 = YConfig({'key1': 'value1'})
    config2 = YConfig({'key2': 'value2'})

    YRegistry.set_config(config1, 'instance1')
    YRegistry.set_config(config2, 'instance2')

    assert YRegistry.get_config('instance1') == config1
    assert YRegistry.get_config('instance2') == config2


def test_empty_templates() -> None:
    """Test handling of empty templates."""
    config = YConfig(
        {
            'empty_env': '${{ env: }}',
            'empty_file': '${{ file: }}',
            'empty_config': '${{ config: }}',
            'empty_yaml': '${{ yaml: }}',
        }
    )

    with pytest.raises(ValueError):
        config.resolve_templates()


def test_special_characters_in_paths() -> None:
    """Test handling of special characters in file paths."""
    # Create temporary file with special characters in name
    special_path = 'tests/config/special@#$%^&*.yaml'
    with open(special_path, 'w') as f:
        f.write('key: value')

    config = YConfig()
    config.add_source(YamlFileSource(special_path))
    assert config['key'] == 'value'

    # Remove temporary file
    os.remove(special_path)


def test_recursive_templates() -> None:
    """Test handling of recursive templates."""
    os.environ['RECURSIVE_VAR'] = '${{ env:FINAL_VAR }}'
    os.environ['FINAL_VAR'] = 'final_value'

    config = YConfig({'recursive': '${{ env:RECURSIVE_VAR }}'})
    config.resolve_templates()
    assert config['recursive'] == 'final_value'

    # Clean up environment variables
    del os.environ['RECURSIVE_VAR']
    del os.environ['FINAL_VAR']


def test_large_file_handling() -> None:
    """Test handling of large files."""
    # Create large temporary file
    large_content = 'key: ' + 'x' * 1000000  # 1MB of data
    with open('tests/config/large.yaml', 'w') as f:
        f.write(large_content)

    config = YConfig()
    config.add_source(YamlFileSource('tests/config/large.yaml'))
    assert len(config['key']) == 1000000

    # Remove temporary file
    os.remove('tests/config/large.yaml')


def test_various_data_types() -> None:
    """Test handling of various data types in configuration."""
    config = YConfig(
        {
            'int_value': 42,
            'float_value': 3.14,
            'bool_value': True,
            'none_value': None,
            'list_value': [1, 2, 3],
            'dict_value': {'nested': 'value'},
            'complex_value': {'list': [{'key': 'value'}, {'key': 'value2'}], 'mixed': [1, 'string', True, None]},
        }
    )

    assert isinstance(config['int_value'], int)
    assert isinstance(config['float_value'], float)
    assert isinstance(config['bool_value'], bool)
    assert config['none_value'] is None
    assert isinstance(config['list_value'], list)
    assert isinstance(config['dict_value'], YNode)
    assert isinstance(config['complex_value']['list'][0], YNode)


def test_getattr_with_list() -> None:
    """Test __getattr__ with list values."""
    config = YNode({'list': [{'key': 'value1'}, {'key': 'value2'}]})
    result = config.list
    assert isinstance(result, list)
    assert isinstance(result[0], YNode)
    assert result[0]['key'] == 'value1'
    assert result[1]['key'] == 'value2'


def test_getitem_with_list() -> None:
    """Test __getitem__ with list values."""
    config = YNode({'nested': {'list': [{'key': 'value1'}, {'key': 'value2'}]}})
    result = config['nested.list']
    assert isinstance(result, list)
    assert isinstance(result[0], YNode)
    assert result[0]['key'] == 'value1'
    assert result[1]['key'] == 'value2'


def test_setitem_with_nested_dict() -> None:
    """Test __setitem__ with nested dictionary creation."""
    config = YConfig()
    config['nested.deep.key'] = 'value'
    assert config['nested.deep.key'] == 'value'
    assert isinstance(config['nested'], YNode)
    assert isinstance(config['nested.deep'], YNode)


def test_resolve_value_with_yaml_in_string() -> None:
    """Test _resolve_value with yaml template in string."""
    config = YConfig({'template': 'prefix ${{ yaml:tests/config/config.yaml }} suffix'})
    with pytest.raises(ValueError, match='YAML template cannot be used inside string'):
        config.resolve_templates()


def test_handle_yaml_with_invalid_file() -> None:
    """Test _handle_yaml with invalid YAML file."""
    config = YConfig()
    with pytest.raises(FileNotFoundError):
        config._handle_yaml('nonexistent.yaml')


def test_config_factory_with_nonexistent_key() -> None:
    """Test YConfigFactory with nonexistent key."""
    with pytest.raises(KeyError):
        YRegistry.get_config('nonexistent')


def test_yconfig_eq_repr_and_constructor() -> None:
    # __eq__ с несовместимым типом
    node = YNode({'a': 1})
    assert node != 12345
    # __repr__
    assert repr(node) == "YNode({'a': 1})"
    # YConfig(data=None)
    cfg = YConfig()
    assert isinstance(cfg, YConfig)


def test_resolve_node_else_branch() -> None:
    cfg = YConfig()
    # _resolve_node с int
    assert cfg._resolve_node(123) == 123


def test_resolve_value_else_branch() -> None:
    cfg = YConfig()
    # _resolve_value без шаблона, просто строка
    assert cfg._resolve_value('plain string') == 'plain string'


def test_handle_file_not_found() -> None:
    cfg = YConfig()
    with pytest.raises(FileNotFoundError):
        cfg._handle_file('no_such_file.txt')


def test_handle_yaml_not_found() -> None:
    cfg = YConfig()
    with pytest.raises(FileNotFoundError):
        cfg._handle_yaml('no_such_file.yaml')


def test_ynode_eq_false_branch() -> None:
    node = YNode({'a': 1})
    assert not (node == 'string')


def test_ynode_repr() -> None:
    node = YNode({'x': 42})
    assert repr(node) == "YNode({'x': 42})"


def test_resolve_node_else_none() -> None:
    cfg = YConfig()
    assert cfg._resolve_node(None) is None


def test_resolve_value_else() -> None:
    cfg = YConfig()
    assert cfg._resolve_value('no template here') == 'no template here'


def test_ynode_eq_with_complex_types() -> None:
    """Test YNode.__eq__ with complex types."""
    node = YNode({'a': 1})
    assert not (node == 42)  # Compare with number
    assert not (node == [1, 2, 3])  # Compare with list
    assert not (node == {'b': 2})  # Compare with dict
    assert node is not None  # Compare with None


def test_ynode_repr_with_complex_data() -> None:
    """Test YNode.__repr__ with complex data structures."""
    complex_data = {'nested': {'list': [1, 2, 3], 'dict': {'key': 'value'}, 'none': None, 'bool': True}}
    node = YNode(complex_data)
    assert repr(node) == f'YNode({complex_data})'


def test_resolve_value_with_complex_templates() -> None:
    """Test _resolve_value with complex template patterns."""
    cfg = YConfig()
    # Test с env шаблоном — ожидаем ValueError, если переменная не задана
    with pytest.raises(ValueError):
        cfg._resolve_value('${{ env:VAR }}')
    # Остальные проверки
    assert cfg._resolve_value('plain text') == 'plain text'
    assert cfg._resolve_value('${{ invalid }}') == '${{ invalid }}'
    assert cfg._resolve_value('${{ }}') == '${{ }}'


def test_handle_file_with_special_paths() -> None:
    """Test _handle_file with special file paths."""
    cfg = YConfig()
    with pytest.raises(FileNotFoundError):
        cfg._handle_file('/nonexistent/path/to/file.txt')
    with pytest.raises(FileNotFoundError):
        cfg._handle_file('../../nonexistent/file.txt')
    with pytest.raises(FileNotFoundError):
        cfg._handle_file('file with spaces.txt')


def test_handle_yaml_with_special_paths() -> None:
    """Test _handle_yaml with special YAML file paths."""
    cfg = YConfig()
    with pytest.raises(FileNotFoundError):
        cfg._handle_yaml('/nonexistent/path/to/config.yaml')
    with pytest.raises(FileNotFoundError):
        cfg._handle_yaml('../../nonexistent/config.yaml')
    with pytest.raises(FileNotFoundError):
        cfg._handle_yaml('config with spaces.yaml')


def test_cov_ynode_eq_false() -> None:
    node = YNode({'a': 1})
    assert not (node == 12345)
    assert not (node == 'abc')
    assert not (node == [1, 2])
    assert node is not None


def test_cov_resolve_node_else() -> None:
    cfg = YConfig()
    assert cfg._resolve_node(123) == 123
    assert cfg._resolve_node('abc') == 'abc'
    assert cfg._resolve_node(True) is True


def test_cov_resolve_value_else() -> None:
    cfg = YConfig()
    assert cfg._resolve_value('no template here') == 'no template here'


def test_cov_handle_file_not_found() -> None:
    cfg = YConfig()
    with pytest.raises(FileNotFoundError):
        cfg._handle_file('definitely_no_such_file.txt')


def test_cov_handle_yaml_not_found() -> None:
    cfg = YConfig()
    with pytest.raises(FileNotFoundError):
        cfg._handle_yaml('definitely_no_such_file.yaml')


def test_getattr_invalid_attribute() -> None:
    node = YNode({'a': 1})
    with pytest.raises(AttributeError, match="'YNode' object has no attribute 'b'"):
        _ = node.b


def test_resolve_templates_list_branch() -> None:
    cfg = YConfig({'list': ['x', 'y']})
    cfg.resolve_templates()
    assert cfg['list'] == ['x', 'y']


def test_embedded_file_template_in_string(tmp_path: Path = Path('tests/config')) -> None:
    # создаём временный файл с содержимым
    file = tmp_path / 'embed.txt'
    file.write_text('HELLO')
    cfg = YConfig({'text': f'prefix ${{{{ file:{file.as_posix()} }}}} suffix'})
    cfg.resolve_templates()
    assert cfg['text'] == 'prefix HELLO suffix'


def test_unknown_action_in_string_raises_value_error() -> None:
    cfg = YConfig({'text': 'foo ${{ unknown:val }} bar'})
    with pytest.raises(ValueError, match='Unknown action in template: unknown'):
        cfg.resolve_templates()


def test_file_decode_error_raises_unicode_decode_error(tmp_path: Path = Path('tests/config')) -> None:
    # файл с некорректными UTF-8 байтами
    file = tmp_path / 'binary.bin'
    file.write_bytes(b'\xff\xfe')
    cfg = YConfig({'data': f'${{{{ file:{file.as_posix()} }}}}'})
    with pytest.raises(UnicodeDecodeError):
        cfg.resolve_templates()


def test_yaml_decode_error_in_handle_yaml(tmp_path: Path = Path('tests/config')) -> None:
    # YAML-файл с некорректными UTF-8 байтами
    file = tmp_path / 'binary.yaml'
    file.write_bytes(b'\xff\xfe')
    cfg = YConfig({'data': f'${{{{ yaml:{file.as_posix()} }}}}'})
    with pytest.raises(UnicodeDecodeError):
        cfg.resolve_templates()
