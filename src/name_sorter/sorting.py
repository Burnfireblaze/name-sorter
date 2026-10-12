from __future__ import annotations

from collections.abc import Iterable

from .name import Name


def sort_names(names: Iterable[Name]) -> list[Name]:
    return sorted(names, key=lambda name: name.sort_key)
