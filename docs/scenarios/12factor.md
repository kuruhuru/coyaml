## 12‑factor configs

Build apps that take settings from the environment, with sensible defaults and overlays.

- Keep secrets in environment, not in YAML
- Use `.env` locally (via `EnvFileSource`) and real env in CI/production
- Compose base + env‑specific overlays (see Overlays)


