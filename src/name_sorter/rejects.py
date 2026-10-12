from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path
from typing import Protocol

from .parsing import Reject

ENCODING = "utf-8"


class RejectSink(Protocol):
    def write(self, rejects: Iterable[Reject]) -> None: ...


class FileRejectSink:
    def __init__(self, path: Path, source_description: str) -> None:
        self._path = path
        self._source_description = source_description

    def write(self, rejects: Iterable[Reject]) -> None:
        rejects_list = list(rejects)
        with self._path.open("w", encoding=ENCODING, newline="\n") as handle:
            handle.write(
                f"# {len(rejects_list)} line(s) rejected from {self._source_description}\n"
            )
            for reject in rejects_list:
                handle.write(
                    f"line {reject.line_number}: {reject.reason} "
                    f"(got '{reject.text}')\n"
                )
