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

## Why Coyaml?

Coyaml simplifies common YAML tasks and stays pragmatic:

* **Dot notation access**: `cfg.section.option`
* **Templates that work**: `${{ env:VAR }}`, `${{ file:path }}`, `${{ config:node }}`, `${{ yaml:file }}`
* **Pydantic interop**: convert any node to models via `.to(Model)`
* **Zero‑boilerplate DI**: `@coyaml` + `Annotated[..., YResource]` injects values into any function
* **Smart search**: inject by parameter name, optionally constrained by glob masks (`*`, `**`)

## Quick Start

Install Coyaml:

```bash
pip install coyaml
```

Load and resolve YAML configurations:

```python
from coyaml import YSettings
from coyaml.sources.yaml import YamlFileSource
from coyaml.sources.env import EnvFileSource

cfg = (
    YSettings()
    .add_source(YamlFileSource('config.yaml'))
    .add_source(EnvFileSource('.env'))
)
cfg.resolve_templates()
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

### Using configurations in code

```python
# Access nested configuration
print(cfg.debug.db.url)

# Access environment variables with defaults
print(cfg.debug.db.password)

# Access embedded file content
print(cfg.debug.db.init_script)

# Access YAML-included configurations
print(cfg.app.extra_settings)

# Modify configuration dynamically
cfg.index = 10

# Validate configuration via Pydantic
from pydantic import BaseModel

class AppConfig(BaseModel):
    db_url: str
    extra_settings: dict

app_config = cfg.app.to(AppConfig)
print(app_config)
```

Coyaml resolves templates and references automatically, keeping configs consistent and adaptable.

### Zero‑boilerplate injection

```python
from typing import Annotated
from coyaml import YRegistry, YResource, coyaml

YRegistry.set_config(cfg)

@coyaml(mask='debug.**')
def connect(user: Annotated[str | None, YResource()] = None) -> str | None:
    return user  # found by name within the masked subtree

print(connect())
```

### Quick links

- Docs: https://coyaml.readthedocs.io
- Tutorials: Basic · Templates · Injection · Merging · Registry
- Concepts: YSettings · YNode · Templates · Injection
- API: https://coyaml.readthedocs.io/en/latest/api/modules/

For detailed documentation, more examples, and a complete API reference, visit [Coyaml Documentation](https://coyaml.readthedocs.io).

---

**License**: Apache License 2.0
