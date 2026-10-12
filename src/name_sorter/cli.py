from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from .app import sort_names_from
from .io_adapters import (
    CompositeNameSink,
    FileNameSink,
    FileNameSource,
    StreamNameSink,
)
from .rejects import FileRejectSink

OUTPUT_FILENAME = "sorted-names-list.txt"
REJECTS_FILENAME = "rejected-names.txt"

EXIT_OK = 0
EXIT_PARTIAL = 1
EXIT_MISSING_FILE = 2
EXIT_IO_ERROR = 3


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="name-sorter",
        description=(
            "Sort a list of names by last name, then by given names. "
            f"Prints the sorted names and writes them to ./{OUTPUT_FILENAME}. "
            f"Invalid rows are reported in ./{REJECTS_FILENAME}."
        ),
    )
    parser.add_argument(
        "input_file",
        type=Path,
        help="text file with one name per line",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    arguments = _build_parser().parse_args(argv)

    source = FileNameSource(arguments.input_file)
    valid_sink = CompositeNameSink(
        StreamNameSink(sys.stdout),
        FileNameSink(Path.cwd() / OUTPUT_FILENAME),
    )
    reject_sink = FileRejectSink(
        Path.cwd() / REJECTS_FILENAME,
        source_description=str(arguments.input_file),
    )

    try:
        reject_count = sort_names_from(source, valid_sink, reject_sink)
    except FileNotFoundError:
        print(f"name-sorter: no such file: {arguments.input_file}", file=sys.stderr)
        return EXIT_MISSING_FILE
    except IsADirectoryError:
        print(
            f"name-sorter: expected a file, got a directory: {arguments.input_file}",
            file=sys.stderr,
        )
        return EXIT_MISSING_FILE
    except PermissionError as error:
        print(
            f"name-sorter: cannot read {error.filename}: permission denied",
            file=sys.stderr,
        )
        return EXIT_MISSING_FILE
    except UnicodeDecodeError:
        print(
            f"name-sorter: {arguments.input_file} is not a valid UTF-8 text file",
            file=sys.stderr,
        )
        return EXIT_MISSING_FILE
    except OSError as error:
        print(
            f"name-sorter: cannot write output: {error}",
            file=sys.stderr,
        )
        return EXIT_MISSING_FILE

    if reject_count:
        print(
            f"name-sorter: {reject_count} line(s) rejected; see ./{REJECTS_FILENAME}",
            file=sys.stderr,
        )
        return EXIT_PARTIAL

    return EXIT_OK
