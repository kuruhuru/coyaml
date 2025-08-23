## Merge semantics

Coyaml applies sources in order. For overlapping keys:

- Dictionaries are merged deeply
- Lists are replaced by the later source
- Scalars are overridden by the later source

See tutorial: [Merging](../tutorials/04_merging.md).


