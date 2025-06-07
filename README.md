# YAMPYC Config

`yampyc` is a package for configuration management in Python projects. It supports
YAML files, `.env` files, environment variables, file contents and external YAML
files. The library also provides dot notation for nested parameters, a singleton
factory and conversion to Pydantic models.

## Table of Contents
- [Installation](#installation)
- [Features](#features)
- [Usage](#usage)
- [Testing](#testing)

## Installation
Add the following to your `pyproject.toml`:

```toml
[tool.uv]
extra-index-url = [
    "https://nexusrepo.smart-consulting.ru/repository/pypi-group/simple",
]
```

Then install the package:

```bash
uv add yampyc
```

## Features
- Template processing after loading the YAML configuration.
- Supported template actions:
  - **env** – insert environment variables.
  - **file** – insert file contents.
  - **config** – insert values from the current configuration.
  - **yaml** – load and insert an external YAML file.
- Recursive template handling.
- Dot notation access to configuration values.
- Conversion to Pydantic models.

## Usage
```python
from yampyc import Yampyc, YampycFactory

config = Yampyc()
config.add_yaml_source('config.yaml')
config.add_env_source('.env')
config.resolve_templates()

# Register and get configuration via the factory
YampycFactory.set_config(config)
conf = YampycFactory.get_config()

# Access values
database_url = conf['debug.db.url']
```

### Iteration and `to_dict`
```python
for key in config:
    print(key)

config_dict = config.to_dict()
```

## Testing
Run tests with `pytest`:
```bash
pytest
```
