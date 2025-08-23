## Injection

This tutorial demonstrates value injection via `@coyaml` and `Annotated[..., YResource]`.

### Explicit path

```python
--8<-- "examples/injection/20_inject_by_explicit_path.py"
```

### By name without mask (whole tree)

```python
--8<-- "examples/injection/21_inject_by_name_no_mask.py"
```

### By name with mask

```python
--8<-- "examples/injection/22_inject_by_name_with_mask.py"
```

### Optional and default None

```python
--8<-- "examples/injection/23_inject_optional_and_defaults.py"
```

### Pydantic model and YNode passthrough

```python
--8<-- "examples/injection/24_inject_pydantic_and_ynode.py"
```

### Ambiguous matches and errors

```python
--8<-- "examples/injection/25_inject_ambiguous_and_errors.py"
```


