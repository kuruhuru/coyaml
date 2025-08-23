## Security

Best practices when using Coyaml:

- Keep secrets in environment variables; avoid committing secrets to YAML
- Use `.env` only for local development; prefer real env in CI/production
- Treat `file:` templates as trusted inputs; avoid reading untrusted paths
- Avoid printing full configs with secrets in logs
- If you need stricter controls, restrict base directories for `file:` and `yaml:` includes at your app level


