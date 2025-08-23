## Splitting configurations

Split large configs into smaller files and include them via `${{ yaml:... }}`.

- Keep domain configs in separate YAMLs
- Reference them from the main file using `yaml:` template
- The included YAML is resolved recursively


