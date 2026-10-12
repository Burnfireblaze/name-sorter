from __future__ import annotations

from collections.abc import Iterable, Iterator
from dataclasses import dataclass

from .name import InvalidNameError, Name


@dataclass(frozen=True, slots=True)
class Reject:
    line_number: int
    text: str
    reason: str


def parse_name(text: str) -> Name:
    parts = text.split()
    if not parts:
        raise InvalidNameError("a name cannot be blank")
    *given_names, last_name = parts
    return Name(given_names=tuple(given_names), last_name=last_name)


def parse_lines(lines: Iterable[str]) -> Iterator[Name | Reject]:
    for line_number, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        try:
            yield parse_name(line)
        except InvalidNameError as error:
            yield Reject(line_number, line.strip(), str(error))
