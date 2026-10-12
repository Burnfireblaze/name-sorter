from __future__ import annotations

from .io_adapters import NameSink, NameSource
from .parsing import Reject, parse_lines
from .rejects import RejectSink
from .sorting import sort_names


def sort_names_from(
    source: NameSource,
    valid_sink: NameSink,
    reject_sink: RejectSink,
) -> int:
    valid = []
    rejects = []
    for item in parse_lines(source.lines()):
        if isinstance(item, Reject):
            rejects.append(item)
        else:
            valid.append(item)

    valid_sink.write(sort_names(valid))

    if rejects:
        reject_sink.write(rejects)

    return len(rejects)
