## Templates

Coyaml replaces placeholders inside strings after `resolve_templates()`:

- `${{ env:VAR[:DEFAULT] }}` — environment variables
- `${{ file:PATH }}` — embed file contents (UTF‑8)
- `${{ config:PATH.TO.NODE }}` — reference a value from the current config
- `${{ yaml:PATH }}` — load and merge external YAML and resolve its templates recursively

### Notes

- Resolution repeats until no templates are left in the resulting string
- `config` returning dict/list inside a string raises `ValueError`
- `yaml` cannot be used inside a string; use it as a standalone value
- Missing env variable without default raises `ValueError`
- Missing files raise `FileNotFoundError`

See tutorials for concrete examples.


