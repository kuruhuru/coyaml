## YNode

`YNode` represents a node (dict or list) with convenient access:

- Attribute access for dict keys
- Dotted indexing for deep paths
- Stable iteration over keys/items/values
- Equality with dict/list for easy testing

### Lists and nesting

```python
node = cfg.debug  # YNode
assert isinstance(node.db, YNode)
items = cfg['list.of.dicts']  # list with YNode elements
```

### Conversion

```python
from pydantic import BaseModel

class App(BaseModel):
    name: str

app = cfg.app.to(App)
```


