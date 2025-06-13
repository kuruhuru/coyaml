# Coyaml

Coyaml is an intuitive Python library designed to simplify YAML configuration management. It lets you split your configurations into smaller files, embed environment variables, and reuse configuration nodes—keeping your settings organized, maintainable, and scalable.

Developed with practical insights from real-world projects, Coyaml is ideal for Python developers who require flexible, powerful, and simple configuration handling.

![Tests](https://github.com/kuruhuru/coyaml/actions/workflows/ci-main.yml/badge.svg)
![Coverage](https://img.shields.io/coveralls/github/kuruhuru/coyaml.svg?branch=main)
![Publish](https://github.com/kuruhuru/coyaml/actions/workflows/publish.yml/badge.svg)
![PyPI](https://img.shields.io/pypi/v/coyaml.svg)
![PyPI - License](https://img.shields.io/pypi/l/coyaml)
![PyPI - Downloads](https://img.shields.io/pypi/dm/coyaml)
---

**Documentation**:  https://coyaml.readthedocs.io

**Source Code**: https://github.com/kuruhuru/coyaml

---

## Why Use Coyaml?

Coyaml simplifies common YAML management tasks:

* **Dot Notation Access**: Easily access nested configuration (`config.section.option`).
* **Pydantic Integration**: Automatic validation and type safety for your settings.
* **Environment Variables**: Direct integration of OS or `.env` variables, with defaults.
* **External File & YAML Inclusion**: Embed file contents and additional YAML files seamlessly.
* **Reusable Nodes**: Reference and reuse YAML configuration sections dynamically.

## Quick Start

Install Coyaml:

```bash
pip install coyaml
```

Load and resolve YAML configurations:

```python
from coyaml import YConfig

config = (
    YConfig()
    .add_yaml_source('config.yaml')
    .add_env_source()
)
config.resolve_templates() # is necessary only when using template placeholders within the YAML configuration.
```

## Example YAML Configuration

```yaml
debug:
  db:
    url: "postgres://user:password@localhost/dbname"
    user: ${{ env:DB_USER }}
    password: ${{ env:DB_PASSWORD:strong:/-password }}
    init_script: ${{ file:tests/config/init.sql }}
llm: "path/to/llm/config"
index: 9
stream: true
app:
  db_url: "postgresql://${{ config:debug.db.user }}:${{ config:debug.db.password }}@localhost:5432/app_db"
  extra_settings: ${{ yaml:tests/config/extra.yaml }}
```

### Using Configurations in Code

```python
# Access nested configuration
print(config.debug.db.url)

# Access environment variables with defaults
print(config.debug.db.password)

# Access embedded file content
print(config.debug.db.init_script)

# Access YAML-included configurations
print(config.app.extra_settings)

# Modify configuration dynamically
config.index = 10

# Validate configuration via Pydantic
from pydantic import BaseModel

class AppConfig(BaseModel):
    db_url: str
    extra_settings: dict

app_config = config.app.to(AppConfig)
print(app_config)
```

Coyaml resolves references automatically, ensuring your configurations remain consistent and adaptable.

For detailed documentation, more examples, and a complete API reference, visit [Coyaml Documentation](https://coyaml.readthedocs.io).

---

**License**: Apache License 2.0
