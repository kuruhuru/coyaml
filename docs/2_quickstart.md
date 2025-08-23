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

Notes:
- Sources are applied in order: later sources override earlier ones.
- Call `resolve_templates()` after all sources are added to process `${{ env|file|config|yaml:… }}`.
- You can mix URIs and manual sources as needed.

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

### Quick injection taste: by name with mask

You can also inject by parameter name. Add an optional `mask` on the decorator to constrain the search to a subtree.

```python
from typing import Annotated
from coyaml import YResource, coyaml

@coyaml(mask='debug.**')
def connect(user: Annotated[str | None, YResource()] = None) -> str | None:
    return user  # 'debug.db.user' will be found by name within the masked subtree

print(connect())
```

Notes:
- If nothing is found and the parameter is `Optional[...]` or has default `None`, `None` is injected.
- If multiple matches are found and `unique=True` (default), an error points to candidate paths; restrict the `mask` or use an explicit path.

## Merge semantics at a glance

- Dictionaries are deep-merged (nested keys are merged recursively).
- Lists are replaced by the later source (no per-item merge).

See the dedicated tutorial: [Merging](tutorials/04_merging.md).

That's it — happy coding!
