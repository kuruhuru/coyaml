Coyaml — a copilot library for effortless YAML management using dot notation. It offers a gentle learning curve with advanced features: Pydantic validation, environment variable resolution (with defaults), file and external YAML inclusion, recursive template resolution, and dependency injection via function or class paths in YAML.

## Table of Contents

* [Installation](#installation)
* [Key Features](#key-features)

  * [Dot Notation Access](#dot-notation-access)
  * [Pydantic Integration](#pydantic-integration)
  * [Environment Variables](#environment-variables)
  * [File Content Insertion](#file-content-insertion)
  * [External YAML Import](#external-yaml-import)
  * [Template Resolution](#template-resolution)
  * [Dependency Injection](#dependency-injection)
* [Quick Start](#quick-start)
* [API: Core Classes](#api-core-classes)
* [Examples](#examples)
* [License](#license)

## Installation

Install via pip:

```bash
pip install coyaml
```

## Key Features

### Dot Notation Access

Read and write nested keys using attribute or bracket syntax:

```python
from coyaml import YConfig

config = YConfig()
config.add_yaml_source('tests/config/config.yaml')
print(config.debug.db.url)                # attribute-style
print(config['debug.db.url'])             # dot-string key
config['debug.db.url'] = 'sqlite:///db.sqlite'  # write by key
```

### Pydantic Integration

Convert configuration sections into Pydantic models for type-safe access:

```python
from pydantic import BaseModel
from coyaml import YConfig

class DebugConfig(BaseModel):
    db: DatabaseConfig

config = YConfig().add_yaml_source('tests/config/config.yaml')
debug: DebugConfig = config.debug.to(DebugConfig)
print(debug.db.url)

# Or convert whole config:
from test_config import AppConfig
app_config: AppConfig = config.to(AppConfig)
print(app_config.llm)
```

### Environment Variables

Use `${{ env:VAR[:default] }}` syntax to inject system or `.env` values with optional defaults:

```yaml
# tests/config/config.yaml
index: 9
DEBUG:
  db:
    user: ${{ env:DB_USER:testuser }}
    password: ${{ env:DB_PASSWORD }}
```

`config.resolve_templates()` will substitute:

* `DB_USER` or use `testuser`
* raise `ValueError` if `DB_PASSWORD` is unset and no default provided

### File Content Insertion

Embed external file contents via `${{ file:path/to/file }}`:

```yaml
init_script: ${{ file:tests/config/init.sql }}
```

### External YAML Import

Merge another YAML file recursively using `${{ yaml:path/to/other.yaml }}`:

```yaml
app:
  extra: ${{ yaml:tests/config/extra.yaml }}
```

### Template Resolution

Support `${{ config:other.key }}` to reference existing config values, nested resolves, and catch missing keys with `KeyError`.

### Dependency Injection

Specify full import paths in YAML and load at runtime:

```yaml
services:
  init: myapp.db.initialize_database
```

```python
fn = config.services.init.to_callable()  # returns function
fn()
```

## Quick Start

```python
from coyaml import YConfig, YConfigFactory

# Create or retrieve singleton
config = YConfig()
YConfigFactory.set_config(config)
config = YConfigFactory.get_config()

# Load sources
config.add_yaml_source('tests/config/config.yaml')
config.add_env_source('tests/config/config.env')

# Resolve all templates (env, file, yaml, config)
config.resolve_templates()

# Access values
i = config.index                  # integer from YAML
env1 = config.ENV1                # from .env
url = config['debug.db.url']

# Validation / conversion
from pydantic import BaseModel
class MySettings(BaseModel):
    index: int
    ENV1: str
settings = config.to(MySettings)
```

## API: Core Classes

* **`YConfig`** — main configuration container

  * `add_yaml_source(path: str) -> YConfig` — load YAML file
  * `add_env_source(path: str = None) -> YConfig` — load `.env` and OS vars
  * `resolve_templates() -> None` — process `env`, `file`, `yaml`, `config` templates
  * `to(model: Type[BaseModel] | str) -> Any` — convert to Pydantic model or import path
  * `get(key: str, value_type: Type[Any] = str) -> Any` — retrieve typed value
  * `set(key: str, value: Any) -> None` — set or override value
  * `__getitem__(key: str) -> Any`, `__setitem__(key: str, value: Any)` — bracket access

* **`YConfigFactory`** — registry for singleton configs

  * `set_config(config: YConfig, key: str = 'default') -> None`
  * `get_config(key: str = 'default') -> YConfig`

* **`YNode`** — node wrapper for dicts and lists

  * Supports iteration: `for k in node`, `node.items()`, `node.values()`

## Examples

1. **Loading YAML & .env**

   ```python
   config = YConfig()
   config.add_yaml_source('tests/config/config.yaml')
   config.add_env_source('tests/config/config.env')
   YConfigFactory.set_config(config)
   config = YConfigFactory.get_config()

   assert config.index == 9
   assert config.ENV1 == '1.0'
   assert config.get('ENV2') == 'String from env file'
   ```

2. **Dot Notation Read/Write**

   ```python
   config['debug.db.url'] = 'sqlite:///local.db'
   assert config.debug.db.url.startswith('sqlite')
   ```

3. **Pydantic Conversion by String**

   ```python
   app_cfg: AppConfig = config.to('test_config.AppConfig')
   ```

4. **Iterate over YNode**

   ```python
   node = YNode({'a': 1, 'b': 2})
   keys = list(node)           # ['a', 'b']
   items = list(node.items())  # [('a', 1), ('b', 2)]
   ```

5. **Error Handling**

   ```python
   try:
       _ = config['non.existent']
   except KeyError:
       print("Missing key raised correctly")
   ```

## License

Apache License 2.0
