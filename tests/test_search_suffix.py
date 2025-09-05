from __future__ import annotations

from coyaml._internal.search import find_by_path_suffix


def test_find_by_path_suffix_basic() -> None:
    data = {'a': {'b': {'c': 1}}, 'x': {'a': {'b': {'c': 2}}}}
    res = find_by_path_suffix(data, 'a.b.c')
    paths = [p for p, _ in res]
    assert paths == ['a.b.c', 'x.a.b.c']


def test_find_by_path_suffix_with_mask() -> None:
    data = {'a': {'b': {'c': 1}}, 'x': {'a': {'b': {'c': 2}}}}
    res = find_by_path_suffix(data, 'a.b.c', masks=['x.**'])
    assert res == [('x.a.b.c', 2)]
