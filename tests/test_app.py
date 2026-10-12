import io
from pathlib import Path

from name_sorter.app import sort_names_from
from name_sorter.io_adapters import FileNameSource, StreamNameSink
from name_sorter.rejects import FileRejectSink


def test_sort_names_from_sorts_and_returns_zero_rejects(tmp_path: Path):
    input_path = tmp_path / "input.txt"
    input_path.write_text("Zoe Smith\nAdam Smith\n", encoding="utf-8")
    source = FileNameSource(input_path)
    buffer = io.StringIO()
    valid_sink = StreamNameSink(buffer)
    reject_sink = FileRejectSink(tmp_path / "rejects.txt", "input.txt")

    reject_count = sort_names_from(source, valid_sink, reject_sink)

    assert reject_count == 0
    assert buffer.getvalue() == "Adam Smith\nZoe Smith\n"


def test_sort_names_from_counts_rejects_and_writes_them(tmp_path: Path):
    input_path = tmp_path / "input.txt"
    input_path.write_text("Marin Alvarez\nSmith\n", encoding="utf-8")
    source = FileNameSource(input_path)
    buffer = io.StringIO()
    reject_path = tmp_path / "rejects.txt"
    valid_sink = StreamNameSink(buffer)
    reject_sink = FileRejectSink(reject_path, "input.txt")

    reject_count = sort_names_from(source, valid_sink, reject_sink)

    assert reject_count == 1
    assert buffer.getvalue() == "Marin Alvarez\n"
    assert "line 2" in reject_path.read_text(encoding="utf-8")
