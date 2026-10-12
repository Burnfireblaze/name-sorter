from pathlib import Path

from name_sorter.parsing import Reject
from name_sorter.rejects import FileRejectSink


def test_reject_sink_writes_header_and_each_reject(tmp_path: Path):
    path = tmp_path / "rejects.txt"
    sink = FileRejectSink(path, source_description="input.txt")
    sink.write(
        [
            Reject(3, "Smith", "no given name"),
            Reject(7, "A B C D E Smith", "too many given names"),
        ]
    )
    content = path.read_text(encoding="utf-8")
    assert "2 line(s) rejected from input.txt" in content
    assert "line 3: no given name (got 'Smith')" in content
    assert "line 7: too many given names (got 'A B C D E Smith')" in content
