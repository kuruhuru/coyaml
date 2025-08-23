## Overlays by environment

Typical layering:

1) `config.yaml` — base
2) `config.dev.yaml` / `config.prod.yaml` — environment overlays
3) `.env` — local developer overrides

Add sources in that order and call `resolve_templates()`.


