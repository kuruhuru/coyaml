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
    """Модель конфигурации базы данных."""

    url: str


class DebugConfig(BaseModel):
    """Модель конфигурации отладки, содержащая конфигурацию базы данных."""

    db: DatabaseConfig


class AppConfig(BaseModel):
    """Основная модель конфигурации приложения, содержащая отладку и LLM параметры."""

    debug: DebugConfig
    llm: str


def test_loading_yaml_and_env_sources() -> None:
    """
    Тест загрузки данных из YAML и .env файлов.
    Проверяет корректность получения данных из разных источников.
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
    """
    Тест конвертации данных конфигурации в Pydantic-модели.
    Проверяет, что конфигурация правильно конвертируется в Pydantic-модель.
    """
    config = Yampyc()
    config.add_yaml_source('tests/config/config.yaml')

    # Конвертация в Pydantic модель
    debug: DebugConfig = config.debug.to(DebugConfig)
    assert debug.db.url == 'postgres://user:password@localhost/dbname', 'Неверный URL базы данных.'

    # Проверка другой модели
    app_config: AppConfig = config.to(AppConfig)
    assert app_config.llm == 'path/to/llm/config', 'Неверная конфигурация LLM.'


def test_assignment_operations() -> None:
    """
    Тест операций присваивания новых параметров в конфигурации.
    Проверяет присваивание значений через атрибуты и точечную нотацию.
    """
    config = Yampyc()
    config.add_yaml_source('tests/config/config.yaml')

    # Пример присваивания значения параметру
    config.index = 10
    assert config.index == 10, "Ошибка присваивания значения 'index'."

    # Присваивание новых параметров
    config.new_param = 'value'
    assert config.new_param == 'value', "Ошибка присваивания нового параметра 'new_param'."

    # Пример работы со словарями и списками
    config.new_param_dict = {'key': 'value'}
    assert config.new_param_dict == {'key': 'value'}, 'Ошибка присваивания словаря.'

    config.new_param_list = [{'key1': 'value1'}, {'key2': 'value2'}]
    assert isinstance(config.new_param_list[0], YampycNode), 'Ошибка присваивания списка словарей.'
    assert config.new_param_list[0]['key1'] == 'value1', 'Ошибка значения в списке словарей.'


def test_dot_notation_access() -> None:
    """
    Тест доступа к конфигурационным параметрам через точечную нотацию.
    Проверяет как чтение, так и запись значений.
    """
    config = Yampyc()
    config.add_yaml_source('tests/config/config.yaml')

    # Проверка чтения через точечную нотацию
    assert (
        config['debug.db.url'] == 'postgres://user:password@localhost/dbname'
    ), 'Ошибка чтения через точечную нотацию.'

    # Проверка записи через точечную нотацию
    config['debug.db.url'] = 'sqlite:///yampyc.db'
    assert config['debug.db.url'] == 'sqlite:///yampyc.db', 'Ошибка записи через точечную нотацию.'


def test_invalid_key_access() -> None:
    """
    Тест обработки некорректных ключей.
    Проверяет вызов исключения при обращении к несуществующему ключу.
    """
    config = Yampyc()
    config.add_yaml_source('tests/config/config.yaml')

    try:
        config['non.existent.key']
    except KeyError:
        pass
    else:
        raise AssertionError('Ожидалось исключение KeyError при доступе к несуществующему ключу.')


def test_empty_config() -> None:
    """
    Тест работы с пустой конфигурацией.
    Проверяет, что пустая конфигурация не вызывает ошибок при чтении и записи.
    """
    config = Yampyc()

    # Пустая конфигурация не должна иметь никаких ключей
    try:
        config['any.key']
    except KeyError:
        pass
    else:
        raise AssertionError('Ожидалось исключение KeyError при доступе к несуществующему ключу в пустой конфигурации.')

    # Можно добавлять новые ключи
    config['new.key'] = 'value'
    assert config['new.key'] == 'value', 'Ошибка при добавлении нового ключа в пустую конфигурацию.'


def test_to_method_with_string() -> None:
    """
    Тест метода to с передачей строкового пути к классу.
    Проверяет корректную динамическую загрузку класса.
    """
    config = Yampyc()
    config.add_yaml_source('tests/config/config.yaml')

    # Используем строковый путь для загрузки класса AppConfig
    app_config: AppConfig = config.to('test_yampyc.AppConfig')
    assert isinstance(app_config, AppConfig), 'Ошибка загрузки модели через строку.'
    assert app_config.llm == 'path/to/llm/config', 'Ошибка преобразования конфигурации.'


def test_to_method_invalid_class() -> None:
    """
    Тест метода to с передачей некорректного пути к классу.
    Ожидается ImportError.
    """
    config = Yampyc()

    with pytest.raises(ModuleNotFoundError):
        config.to('invalid.module.ClassName')


def test_to_method_invalid_attribute() -> None:
    """
    Тест метода to с передачей некорректного имени класса в существующем модуле.
    Ожидается AttributeError.
    """
    config = Yampyc()

    with pytest.raises(ModuleNotFoundError):
        config.to('yampyc_test.InvalidClassName')
    with pytest.raises(AttributeError):
        config.to('test_yampyc.InvalidClassName')


def test_to_method_with_class() -> None:
    """
    Тест метода to с передачей класса напрямую.
    Проверяет корректное преобразование конфигурации в объект модели.
    """
    config = Yampyc()
    config.add_yaml_source('tests/config/config.yaml')

    app_config = config.to(AppConfig)
    assert isinstance(app_config, AppConfig), 'Ошибка преобразования в объект модели.'
    assert app_config.llm == 'path/to/llm/config', 'Ошибка в данных модели.'


def test_iteration_over_keys() -> None:
    """
    Тест итерации по ключам в YampycNode.
    """
    config = YampycNode({'key1': 'value1', 'key2': 'value2'})

    keys = list(config)
    assert keys == ['key1', 'key2'], 'Ошибка в итерации по ключам.'


def test_iteration_over_items() -> None:
    """
    Тест итерации по ключам и значениям в YampycNode.
    """
    config = YampycNode({'key1': 'value1', 'key2': 'value2'})

    items = list(config.items())
    assert items == [
        ('key1', 'value1'),
        ('key2', 'value2'),
    ], 'Ошибка в итерации по ключам и значениям.'


def test_iteration_over_values() -> None:
    """
    Тест итерации по значениям в YampycNode.
    """
    config = YampycNode({'key1': 'value1', 'key2': 'value2'})

    values = list(config.values())
    assert values == ['value1', 'value2'], 'Ошибка в итерации по значениям.'


def test_parsing_env_vars_in_yaml_with_default() -> None:
    """
    Тест для проверки корректности замены переменных окружения в YAML файле с поддержкой значений по умолчанию.
    """
    # Устанавливаем переменные окружения для теста
    os.environ['DB_USER'] = 'test_user'

    # Важно, чтобы DB_PASSWORD не было установлено в окружении
    if 'DB_PASSWORD' in os.environ:
        del os.environ['DB_PASSWORD']

    config = Yampyc()
    config.add_yaml_source('tests/config/config.yaml')
    config.resolve_templates()

    # Проверка того, что переменные окружения подставились корректно
    assert config['debug.db.user'] == 'test_user', "Ошибка в замене переменной окружения для 'db.user'."
    assert (
        config['debug.db.password'] == 'strong:/-password'
    ), "Ошибка в использовании значения по умолчанию для 'db.password'."

    # Устанавливаем значение DB_PASSWORD и проверяем ещё раз
    os.environ['DB_PASSWORD'] = 'real_password'  # noqa: S105

    config = Yampyc()
    config.add_yaml_source('tests/config/config.yaml')
    config.resolve_templates()

    assert config.debug.db.password == 'real_password', "Ошибка в замене переменной окружения для 'db.password'."  # noqa: S105


def test_missing_env_var_without_default() -> None:
    """
    Тест для проверки обработки ситуации, когда переменная окружения не задана и значение по умолчанию не указано.
    """
    # Убедимся, что переменная окружения не установлена
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
    """
    Тест для проверки корректной обработки всех типов шаблонов в конфигурации.
    """
    # Устанавливаем переменные окружения для теста
    os.environ['DB_USER'] = 'test_user'
    os.environ['DB_PASSWORD'] = 'test_password'  # noqa: S105

    config = Yampyc()
    config.add_yaml_source('tests/config/config.yaml')
    config.resolve_templates()

    # Проверка замены переменных окружения
    assert config['debug.db.user'] == 'test_user', "Ошибка в замене переменной окружения для 'debug.db.user'."
    assert (
        config['debug.db.password'] == 'test_password'
    ), "Ошибка в замене переменной окружения для 'debug.db.password'."

    # Проверка вставки содержимого файла
    with open('tests/config/init.sql') as f:
        init_script_content = f.read()
    assert config['debug.db.init_script'] == init_script_content, "Ошибка в вставке содержимого файла 'init.sql'."

    # Проверка вставки значения из текущей конфигурации
    expected_db_url = f'postgresql://{config["debug.db.user"]}:{config["debug.db.password"]}@localhost:5432/app_db'
    assert config['app.db_url'] == expected_db_url, "Ошибка в вставке значения из текущей конфигурации в 'app.db_url'."

    # Проверка загрузки внешнего YAML файла
    assert (
        config['app.extra_settings.feature_flags.enable_new_feature'] is True
    ), "Ошибка в загрузке внешнего YAML файла и чтении 'enable_new_feature'."
    assert (
        config['app.extra_settings.feature_flags.beta_mode'] is False
    ), "Ошибка в загрузке внешнего YAML файла и чтении 'beta_mode'."


def test_file_not_found() -> None:
    """
    Тест для проверки обработки ситуации, когда файл для вставки не найден.
    """
    # Изменяем путь к файлу на несуществующий
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

    # Удаляем временный файл
    os.remove('tests/config/temp_config.yaml')


def test_yaml_file_not_found() -> None:
    """
    Тест для проверки обработки ситуации, когда внешний YAML файл не найден.
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

    # Удаляем временный файл
    os.remove('tests/config/temp_config.yaml')


def test_invalid_template_action() -> None:
    """
    Тест для проверки обработки ситуации, когда указано неизвестное действие в шаблоне.
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
        match=r'Неизвестное действие в шаблоне: unknown_action',
    ):
        config.resolve_templates()

    # Удаляем временный файл
    os.remove('tests/config/temp_config.yaml')


def test_recursive_template_resolution() -> None:
    """
    Тест для проверки рекурсивной обработки шаблонов.
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

    assert config['app.final_value'] == 'resolved_value', 'Ошибка в рекурсивной обработке шаблонов.'

    # Удаляем временный файл и переменные окружения
    os.remove('tests/config/temp_config.yaml')
    del os.environ['NESTED_ENV']
    del os.environ['FINAL_ENV']


def test_config_key_not_found() -> None:
    """
    Тест для проверки обработки ситуации, когда ключ в конфигурации не найден при использовании шаблона config.
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
        match=r"Ключ 'nonexistent.key' не найден в конфигурации.",
    ):
        config.resolve_templates()

    # Удаляем временный файл
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
