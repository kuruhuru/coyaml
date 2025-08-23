## YSettings

`YSettings` is the core configuration container. It wraps a nested dict and adds:

- Dot notation access (attribute and dotted-key)
- Loading from sources (`add_source(YSource)`)
- Template resolution (`resolve_templates()`)
- Conversion to Pydantic models via `.to(Model)`

### Lifecycle

1) Create an instance
2) Add one or more sources in order (later override earlier)
3) Call `resolve_templates()` once, after all sources are added

```python
from coyaml import YSettings
from coyaml.sources.yaml import YamlFileSource

cfg = YSettings()
cfg.add_source(YamlFileSource('config.yaml'))
cfg.resolve_templates()
```

### Access patterns

```python
cfg.index = 9                   # attribute set
print(cfg.index)                # attribute get
cfg['nested.key'] = 'value'     # dotted key set
print(cfg['nested.key'])        # dotted key get
```

### Convert to models

```python
from pydantic import BaseModel

class DB(BaseModel):
    url: str

db: DB = cfg.debug.db.to(DB)
```


