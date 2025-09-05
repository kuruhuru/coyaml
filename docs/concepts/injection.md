## Injection

Coyaml injects configuration values into functions using `@coyaml` and `Annotated[..., YResource]`.

### Explicit path

```python
from typing import Annotated
from coyaml import YResource, coyaml

@coyaml
def handler(user: Annotated[str, YResource('debug.db.user')]) -> str:
    return user
```

### By name with optional mask

When `YResource` has no path, Coyaml searches by parameter name. Use `mask` to constrain search to dotted paths.

```python
from typing import Annotated
from coyaml import YResource, coyaml

@coyaml(mask='debug.**')
def connect(user: Annotated[str | None, YResource()] = None) -> str | None:
    return user
```

Notes:
- Optional or default `None` → injects `None` when not found
- Multiple matches + `unique=True` (default) → error with candidate paths; restrict the mask or set `unique=False`
- If the value is a `YNode` and the annotation expects a Pydantic model, it is converted via `.to(Model)`

### Relative `path` in `YResource`

You can provide a relative dotted `path` in `YResource(path)` and combine it with a decorator `mask`.

Relative means "suffix match" over full dotted paths, filtered by `mask` first. The first match is injected; if multiple matches exist and `unique=True`, an error is raised with candidates.

```python
from typing import Annotated
from coyaml import YResource, coyaml

@coyaml(mask='env.**')
def handler(svcs: Annotated[dict[str, int] | None, YResource('services')] = None) -> dict[str, int] | None:
    return svcs
```

To force an absolute path, prefix with `^`:

```python
@coyaml
def handler_abs(svcs: Annotated[dict[str, int], YResource('^env.services')]) -> dict[str, int]:
    return svcs
```


