## Testing patterns

- Use `YRegistry.set_config` in a fixture to provide a test snapshot
- Clean up with `YRegistry.remove_config()` to avoid leaking state
- For snapshot testing, compare `cfg.to_dict()` against expected dicts


