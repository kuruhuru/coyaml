# Tutorial: First Steps

<!-- 
1. Define a Pydantic schema for your config  
2. Load your YAML file  
3. Validate and use dot-notation  
4. Access the schema-typed config
-->

```python
from pydantic import BaseModel
from coyaml import YConfig

class DBConfig(BaseModel):
    url: str
    user: str
    password: str

config = YConfig().add_yaml_source("config.yaml")
db: DBConfig = config.database.to(DBConfig)
print(db.url, db.user)
```