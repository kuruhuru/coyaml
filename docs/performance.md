## Performance

Coyaml favors clarity and determinism.

- Template resolution: linear in the number of placeholders
- Search by name: DFS over the tree (use explicit paths for hot paths, or narrow with masks)
- Dict merge: deep recursion; lists: replace

Tips:
- Load and resolve once at startup; reuse the registry snapshot
- Prefer explicit paths in tight loops; use masks to constrain search
- Split large YAML into smaller files to improve locality

Roadmap ideas:
- Optional key index for faster by‑name search
- Incremental reloads and watchers per source


