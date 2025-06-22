# Quickstart

Install Coyaml:

```bash
pip install coyaml
```

## Loading a configuration

The heart of Coyaml is the `YSettings` object — a thin wrapper around a nested `dict` that gives you **dot-notation access**, Pydantic conversion and much more.

```python
from coyaml import YSettings
from coyaml.sources.yaml import YamlFileSource
from coyaml.sources.env import EnvFileSource

cfg = (
    YSettings()
    .add_source(YamlFileSource('config.yaml'))  # ↩ YAML file
    .add_source(EnvFileSource('.env'))          # ↩ environment overrides
)

# 🔄  Replace templates like `${{ env:DB_USER }}`
cfg.resolve_templates()
```

Alternatively, you can build a config with a single call using **URI helpers**:

```python
from coyaml import YRegistry

cfg = YRegistry.create_from_uri_list([
    'yaml://config.yaml',
    'env://.env',
])
```

## Example YAML with templates

```yaml
index: 9
stream: true
llm: "path/to/llm/config"
debug:
  db:
    url: "postgres://user:password@localhost/dbname"
    user: ${{ env:DB_USER }}            # ← env variable
    password: ${{ env:DB_PASSWORD:dev }} # ← with default
    init_script: ${{ file:init.sql }}   # ← embed file content
app:
  db_url: "postgresql://${{ config:debug.db.user }}:${{ config:debug.db.password }}@localhost/app"
  extra_settings: ${{ yaml:extra.yaml }} # ← include another YAML
```

After `resolve_templates()` every placeholder is replaced by its real value.

## Using the config

```python
# Simple attribute access
print(cfg.debug.db.url)

# Convert a node to a Pydantic model
from pydantic import BaseModel

class DBConfig(BaseModel):
    url: str
    user: str
    password: str

print(cfg.debug.db.to(DBConfig))
```

## Zero-boilerplate injection

Coyaml ships with a tiny helper to inject configuration values into **any** function:

```python
from typing import Annotated
from coyaml import YResource, coyaml

@coyaml
def handler(
    user: Annotated[str, YResource('debug.db.user')],
    pwd: Annotated[str, YResource('debug.db.password')],
):
    print(user, pwd)

handler()  # arguments are taken from cfg that lives in YRegistry ("default")
```

That's it — happy coding!
