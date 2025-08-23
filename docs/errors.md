## Error handling

Common exceptions and how to fix them:

- `ValueError: Unknown action in template` — check the action name (supported: env, file, config, yaml)
- `ValueError: Environment variable ... is not set ...` — provide the variable or a default (`${{ env:VAR:default }}`)
- `ValueError: Config template cannot return dict or list inside string` — move the `config:` to a standalone value
- `ValueError: YAML template cannot be used inside string` — use `yaml:` as a value, not inline in a string
- `FileNotFoundError` — verify file path for `file:` or `yaml:` templates
- `KeyError: Key '...' not found in configuration` — check the dotted path for `config:` templates
- `KeyError (injection): Key by name '...' not found` — adjust the decorator `mask` or use an explicit path
- `KeyError (injection): Ambiguous key name '...'` — narrow the `mask` or set `unique=False` or use an explicit path


