from __future__ import annotations

from coyaml._internal.search import _compile_mask


def test_compile_mask_basic() -> None:
    assert _compile_mask('debug.*.user').match('debug.db.user')
    assert not _compile_mask('debug.*.user').match('prod.db.user')


def test_compile_mask_globstar() -> None:
    assert _compile_mask('**.user').match('user')
    assert _compile_mask('**.user').match('a.b.user')
    assert not _compile_mask('**.user').match('a.b.username')
