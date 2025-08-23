## Comparison

How Coyaml compares to popular tools:

### Dynaconf / OmegaConf / Hydra

Pros of Coyaml:
- Minimal API surface; easy to adopt
- Strong template engine (env/file/config/yaml) with recursive resolution
- Framework‑agnostic DI via `@coyaml` and `Annotated` (no app wiring)
- Pydantic conversion built‑in
- Deterministic errors and simple merge rules

Where others are stronger:
- Hydra: powerful composable overrides and rich ecosystem
- OmegaConf: flexible typed configs and interpolation features
- Dynaconf: many built‑in providers and integrations

Pick Coyaml when you want straightforward YAML + pragmatic power without a large framework.


