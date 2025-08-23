## Framework integration

Coyaml is framework‑agnostic. A few tips:

- **FastAPI**: load config at startup, inject values into endpoints with `@coyaml`
- **Click**: configure once in `main`, inject into command functions
- **Django**: wrap settings read in module‑level snapshot and pass values explicitly


