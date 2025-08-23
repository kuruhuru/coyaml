## Migration: YConfig → YSettings

Coyaml keeps legacy `YConfig/YConfigFactory` for compatibility. Prefer `YSettings/YRegistry`.

### Before

```python
from coyaml import YConfig

cfg = (
    YConfig()
    .add_yaml_source('config.yaml')
    .add_env_source()
)
cfg.resolve_templates()
```

### After

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

### Factory → Registry

```python
from coyaml import YRegistry

YRegistry.set_config(cfg)  # default
cfg2 = YRegistry.get_config()
```


