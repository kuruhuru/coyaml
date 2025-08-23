## Dependency injection in applications

Inject config into CLI commands, HTTP handlers, and background jobs using `@coyaml`:

- Use explicit paths for hot paths to avoid search cost
- Use `mask` with by‑name injection to reduce boilerplate in wider modules
- Keep loading at startup; use the registry snapshot during requests


