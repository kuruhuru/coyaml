# Coyaml

Coyaml is a pragmatic Python library for YAML configuration that stays simple for small apps and scales to complex setups.
It gives you clean dot access, powerful templates, zero‑boilerplate injection, and smooth Pydantic interop — without a heavy framework.

![Tests](https://github.com/kuruhuru/coyaml/actions/workflows/ci-main.yml/badge.svg)
![Coverage](https://img.shields.io/coveralls/github/kuruhuru/coyaml.svg?branch=main)
![Publish](https://github.com/kuruhuru/coyaml/actions/workflows/publish.yml/badge.svg)
![PyPI](https://img.shields.io/pypi/v/coyaml.svg)
![PyPI - License](https://img.shields.io/pypi/l/coyaml)
![PyPI - Downloads](https://img.shields.io/pypi/dm/coyaml)

---

## Why Coyaml

- **Simple dot access**: `cfg.section.option` with safe nested creation
- **Templates that work**: `${{ env:VAR }}`, `${{ file:path }}`, `${{ config:node }}`, `${{ yaml:file }}`
- **Pydantic interop**: convert any node to models via `.to(Model)`
- **Zero‑boilerplate DI**: `@coyaml` + `Annotated[..., YResource]` injects values into any function
- **Smart search**: inject by parameter name, optionally constrained by glob masks (`*`, `**`) with deterministic behavior
- **Predictable merge**: dicts deep‑merge, lists are replaced (documented and explicit)

## 10‑second example

```python
from typing import Annotated
from coyaml import YSettings, YRegistry, YResource, coyaml
from coyaml.sources.yaml import YamlFileSource

# Load once
cfg = YSettings().add_source(YamlFileSource('config.yaml'))
cfg.resolve_templates()
YRegistry.set_config(cfg)

# Inject by name, constrained to debug subtree
@coyaml(mask='debug.**')
def connect(user: Annotated[str, YResource()], url: Annotated[str, YResource('debug.db.url')]):
    print(user, url)

connect()
```

- Works with environment variables, files, and external YAML includes
- Deterministic and helpful errors (missing, ambiguous, invalid templates)

## Quick Links

- [Installation](1_installation.md)
- [Quickstart](2_quickstart.md)
- [Tutorials: Basic](tutorials/01_basic.md) · [Templates](tutorials/02_templates.md) · [Injection](tutorials/03_injection.md) · [Merging](tutorials/04_merging.md) · [Registry](tutorials/05_registry.md)
- [API Reference](api/modules.md)
- [Changelog](CHANGELOG.md)
