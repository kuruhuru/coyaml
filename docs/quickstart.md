# Quickstart

<!-- 
Step-by-step minimal example:
1. Import and configure `YConfig` / `YConfigFactory`
2. Add YAML and .env sources
3. Resolve templates
4. Access values via attributes or dot-notation
5. Convert to a Pydantic model
-->

```python
from coyaml import YConfig, YConfigFactory

# 1. Initialize
config = YConfig()
YConfigFactory.set_config(config)

# 2. Load sources
config.add_yaml_source("path/to/config.yaml")
config.add_env_source("path/to/.env")

# 3. Resolve templates
config.resolve_templates()

# 4. Access values
print(config.some.setting)
print(config["another.setting"])

# 5. Convert to Pydantic
from pydantic import BaseModel

class Settings(BaseModel):
    some: str
    another: int

settings = config.to(Settings)
print(settings)
```