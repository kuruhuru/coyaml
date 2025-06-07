# YAMPYC Config

`yampyc` is a package for managing configurations in projects. It provides convenient tools for working with configurations, supporting data sources such as YAML files, `.env` files, environment variables, text file contents, and external YAML files. The library also supports using dot notation for accessing nested parameters, working with singletons, and converting data to Pydantic models.

## Table of Contents

- [YAMPYC Config](#yampyc-config)
  - [Table of Contents](#table-of-contents)
  - [Installation](#installation)
  - [Main Features](#main-features)
    - [New Template Processing Mechanism](#new-template-processing-mechanism)
    - [Supported Template Actions](#supported-template-actions)
      - [Environment Variable Insertion (`env`)](#environment-variable-insertion-env)
      - [File Content Insertion (`file`)](#file-content-insertion-file)
      - [Configuration Value Insertion (`config`)](#configuration-value-insertion-config)
      - [External YAML File Loading (`yaml`)](#external-yaml-file-loading-yaml)
    - [Recursive Template Processing](#recursive-template-processing)
  
## Installation

```bash
pip install yampyc
```

## Main Features

### New Template Processing Mechanism

The library supports a powerful template processing mechanism that allows you to:

- Insert environment variable values
- Insert text file contents
- Insert values from the current configuration
- Load and insert external YAML files

### Supported Template Actions

#### Environment Variable Insertion (`env`)

Inserts the value of an environment variable.

**Syntax:**

```yaml
${{ env:VARIABLE_NAME[:DEFAULT_VALUE] }}
```

**Example:**

```yaml
database:
  user: ${{ env:DB_USER }}
  password: ${{ env:DB_PASSWORD:default_password }}
```

#### File Content Insertion (`file`)

Inserts the content of a text file.

**Syntax:**

```yaml
${{ file:PATH_TO_FILE }}
```

**Example:**

```yaml
init_script: ${{ file:./scripts/init.sql }}
```

#### Configuration Value Insertion (`config`)

Inserts a value from the current configuration.

**Syntax:**

```yaml
${{ config:PATH.TO.NODE }}
```

**Example:**

```yaml
db_url: "postgresql://${{ config:database.user }}:${{ config:database.password }}@localhost:5432/app_db"
```

#### External YAML File Loading (`yaml`)

Loads and inserts the content of an external YAML file.

**Syntax:**

```yaml
${{ yaml:PATH_TO_YAML_FILE }}
```

**Example:**

```yaml
extra_settings: ${{ yaml:./configs/extra.yaml }}
```

### Recursive Template Processing

Templates can be nested within each other. Processing will be performed recursively until all templates are fully resolved.

**Example:**

```yaml
nested_value: ${{ env:NESTED_ENV }}
final_value: ${{ config:nested_value }}
```

If the environment variable `NESTED_ENV` contains another template, it will also be processed.

## Usage

### Creating Configuration

To start working with configuration, create an instance of the `Yampyc` class:

```python
from yampyc import Yampyc

config = Yampyc()
```

### Loading Data from YAML File

Load data from a YAML file:

```python
config.add_yaml_source('config.yaml')
```

### Loading Data from .env File

Load data from a `.env` file:

```python
config.add_env_source('.env')
```

### Processing Templates

After loading all configuration sources, you need to call the `resolve_templates()` method to process all templates in the configuration:

```python
config.resolve_templates()
```

### Working with Configuration Data

Access to configuration parameters is possible both through attributes and through keys:

```python
database_url = config.database.url  # through attributes
database_url = config['database.url']  # through dot notation
```

### Using Dot Notation

You can use dot notation to access nested configuration parameters:

```python
config['debug.db.url'] = "sqlite:///yampyc.db"
assert config['debug.db.url'] == "sqlite:///yampyc.db"
```

### Using Configuration Factory

For working with configuration singletons, use the `YampycFactory`:

```python
from yampyc import YampycFactory

# Setting configuration in factory
YampycFactory.set_config(config)

# Getting configuration from factory
singleton_config = YampycFactory.get_config()
```

### Converting to Pydantic Models

Configuration can be converted to Pydantic models:

```python
from pydantic import BaseModel

class DatabaseConfig(BaseModel):
    url: str

db_config = config.database.to(DatabaseConfig)
print(f"Database URL from model: {db_config.url}")
```

### Iterating Over Configuration Node

You can iterate over keys, values, or key-value pairs in the configuration, like in a dictionary:

```python
# Iterating over keys
for key in config:
    print(key)

# Iterating over keys and values
for key, value in config.items():
    print(f"{key}: {value}")

# Iterating over values
for value in config.values():
    print(value)
```

### `to_dict` Method

You can convert a configuration node to a dictionary:

```python
config_dict = config.to_dict()
print(config_dict)
```

---

**Important:** After loading configuration from YAML and `.env` files, be sure to call `config.resolve_templates()` to ensure all templates are processed and replaced with real values.

**Note:** Make sure all files specified in templates exist, and environment variables are set or have default values to avoid errors during template processing.

If you have any questions or issues while using `yampyc`, please refer to the documentation or create an issue in the project repository.