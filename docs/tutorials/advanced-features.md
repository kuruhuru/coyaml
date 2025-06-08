# Tutorial: Advanced Features

<!-- 
Cover:
- Nested template resolution
- File inclusion
- YAML inclusion
- Environment defaults & error modes
- Converting config entries to callables
-->

## Environment Variables

- Syntax: `${{ env:VAR[:DEFAULT] }}`
- Behavior when missing / default provided

## File & YAML Inclusion

- `${{ file:path/to.txt }}`
- `${{ yaml:other_config.yaml }}`

## Callable Injection

```yaml
services:
  init: myapp.db.initialize_database
```

```python
fn = config.services.init.to_callable()
fn()
```


