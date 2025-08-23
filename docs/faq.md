## FAQ

### Why are lists replaced instead of merged?
Coyaml keeps list semantics simple and explicit. Use full replacement to avoid surprising merges.

### When should I call `resolve_templates()`?
After all sources are added, once per config lifecycle.

### Can I load multiple YAML files?
Yes, add multiple `YamlFileSource` in order, or include via `${{ yaml:... }}`.

### How do I use Pydantic models?
Call `.to(Model)` on any node (or the root). Models validate values and types.

### Explicit path vs by‑name injection?
Use explicit paths on hot paths and when you want total clarity. Use by‑name with a `mask` to reduce boilerplate in wider modules; handle ambiguity by narrowing masks.


