## Merging

Coyaml merges sources in the order they are added. Later sources override earlier ones.
Dictionaries are merged deeply; lists are replaced.

### Multiple sources and order

```python
--8<-- "examples/merging/30_multi_source_merge_order.py"
```

### Lists semantics

```python
--8<-- "examples/merging/31_lists_and_merge_semantics.py"
```


