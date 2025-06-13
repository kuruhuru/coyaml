# Quickstart

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
