## Sources

Coyaml loads data from sources implementing `YSource`:

- `YamlFileSource(path)` — load from YAML file
- `EnvFileSource(path | None)` — load environment variables, optionally from `.env`

Add sources in order; later ones override earlier ones. Call `resolve_templates()` after adding them.

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


