from __future__ import annotations

from collections.abc import Iterable, Iterator
from pathlib import Path
from typing import Protocol, TextIO

from .name import Name

ENCODING = "utf-8"


class NameSource(Protocol):
    def lines(self) -> Iterator[str]: ...


class NameSink(Protocol):
    def write(self, names: Iterable[Name]) -> None: ...


class FileNameSource:
    def __init__(self, path: Path) -> None:
        self._path = path

    def lines(self) -> Iterator[str]:
        with self._path.open(encoding=ENCODING) as handle:
            yield from handle


class StreamNameSink:
    def __init__(self, stream: TextIO) -> None:
        self._stream = stream

    def write(self, names: Iterable[Name]) -> None:
        for name in names:
            print(name, file=self._stream)


class FileNameSink:
    def __init__(self, path: Path) -> None:
        self._path = path

    def write(self, names: Iterable[Name]) -> None:
        with self._path.open("w", encoding=ENCODING, newline="\n") as handle:
            for name in names:
                handle.write(f"{name}\n")


class CompositeNameSink:
    def __init__(self, *sinks: NameSink) -> None:
        self._sinks = sinks

    def write(self, names: Iterable[Name]) -> None:
        materialised = list(names)
        for sink in self._sinks:
            sink.write(materialised)
