## Examples

Coyaml includes runnable examples in the repository root under `examples/`.

### Running the examples

1. Ensure you have a working environment (optional but recommended):

```bash
uv run python -c "import sys; print(sys.version)"
```

2. Run the basic example:

```bash
PYTHONPATH=src uv run python examples/base.py
```

This will:
- load configuration from `examples/config/config.yaml`
- resolve templates (`env`, `file`, `config`, `yaml`)
- inject values into functions decorated with `@coyaml`

### What to look at

- `examples/base.py`: small end-to-end demo using `YSettings`, DI via `@coyaml`, and Pydantic models
- `examples/config/config.yaml`: configuration file showcasing templates and nesting


