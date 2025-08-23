## Registry

`YRegistry` stores named configuration instances (e.g., `default`, `dev`, `prod`).

```python
from coyaml import YSettings, YRegistry

YRegistry.set_config(YSettings({'value': 1}), 'dev')
YRegistry.set_config(YSettings({'value': 2}), 'prod')

print(YRegistry.get_config('dev')['value'])
```

Always remove configs in tests/demos to avoid state bleed:

```python
YRegistry.remove_config('dev')
```


