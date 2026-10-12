import io
from pathlib import Path

from name_sorter.io_adapters import (
    CompositeNameSink,
    FileNameSink,
    FileNameSource,
    StreamNameSink,
)
from name_sorter.name import Name


def test_file_source_yields_lines(tmp_path: Path):
    path = tmp_path / "input.txt"
    path.write_text("Marin Alvarez\nLeo Gardner\n", encoding="utf-8")
    source = FileNameSource(path)
    assert list(source.lines()) == ["Marin Alvarez\n", "Leo Gardner\n"]


def test_stream_sink_writes_names_one_per_line():
    buffer = io.StringIO()
    sink = StreamNameSink(buffer)
    sink.write([Name(("Marin",), "Alvarez"), Name(("Leo",), "Gardner")])
    assert buffer.getvalue() == "Marin Alvarez\nLeo Gardner\n"


def test_file_sink_overwrites_existing_file(tmp_path: Path):
    path = tmp_path / "out.txt"
    path.write_text("stale content\n", encoding="utf-8")
    sink = FileNameSink(path)
    sink.write([Name(("Marin",), "Alvarez")])
    assert path.read_text(encoding="utf-8") == "Marin Alvarez\n"


def test_composite_sink_writes_to_all_underlying_sinks():
    buffer1 = io.StringIO()
    buffer2 = io.StringIO()
    composite = CompositeNameSink(StreamNameSink(buffer1), StreamNameSink(buffer2))
    composite.write([Name(("Marin",), "Alvarez")])
    assert buffer1.getvalue() == "Marin Alvarez\n"
    assert buffer2.getvalue() == "Marin Alvarez\n"
