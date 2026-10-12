from pathlib import Path

from name_sorter.cli import EXIT_MISSING_FILE, EXIT_OK, EXIT_PARTIAL, main
from tests.conftest import BRIEF_EXAMPLE_INPUT, BRIEF_EXAMPLE_OUTPUT

OUTPUT_FILENAME = "sorted-names-list.txt"
REJECTS_FILENAME = "rejected-names.txt"


def _write_input(directory: Path, lines: list[str]) -> Path:
    path = directory / "unsorted-names-list.txt"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def test_prints_and_writes_sorted_names(working_directory, capsys):
    path = _write_input(working_directory, BRIEF_EXAMPLE_INPUT)

    exit_code = main([str(path)])

    assert exit_code == EXIT_OK
    assert capsys.readouterr().out.splitlines() == BRIEF_EXAMPLE_OUTPUT
    output_file = working_directory / OUTPUT_FILENAME
    assert output_file.read_text(encoding="utf-8").splitlines() == BRIEF_EXAMPLE_OUTPUT


def test_overwrites_existing_output_file(working_directory):
    (working_directory / OUTPUT_FILENAME).write_text("stale\n", encoding="utf-8")
    path = _write_input(working_directory, BRIEF_EXAMPLE_INPUT)

    main([str(path)])

    assert "stale" not in (working_directory / OUTPUT_FILENAME).read_text(
        encoding="utf-8"
    )


def test_reports_missing_input_file(working_directory, capsys):
    exit_code = main([str(working_directory / "nope.txt")])

    assert exit_code == EXIT_MISSING_FILE
    assert "no such file" in capsys.readouterr().err


def test_rejects_bad_lines_but_still_writes_valid_output(working_directory, capsys):
    path = _write_input(
        working_directory,
        ["Janet Parsons", "Smith", "A B C D E Jones", "Leo Gardner"],
    )

    exit_code = main([str(path)])

    assert exit_code == EXIT_PARTIAL
    output = (working_directory / OUTPUT_FILENAME).read_text(encoding="utf-8")
    assert output.splitlines() == ["Leo Gardner", "Janet Parsons"]
    rejects = (working_directory / REJECTS_FILENAME).read_text(encoding="utf-8")
    assert "line 2" in rejects
    assert "line 3" in rejects
    stderr = capsys.readouterr().err
    assert "2 line(s) rejected" in stderr


def test_handles_a_thousand_names(working_directory):
    lines = [f"Given{i:04d} Last{(1000 - i):04d}" for i in range(1000)]
    path = _write_input(working_directory, lines)

    exit_code = main([str(path)])

    assert exit_code == EXIT_OK
    written = (
        (working_directory / OUTPUT_FILENAME).read_text(encoding="utf-8").splitlines()
    )
    assert written == sorted(lines, key=lambda line: line.split()[1])


def test_preserves_unicode_names_in_output(working_directory):
    path = _write_input(
        working_directory,
        ["Zoe Smith", "José Álvarez", "Jose Alvarez"],
    )

    main([str(path)])

    output = (working_directory / OUTPUT_FILENAME).read_text(encoding="utf-8")
    lines = output.splitlines()

    # Both Alvarez variants come first (same normalized key), Smith last.
    assert "Álvarez" in lines[0] or "Álvarez" in lines[1]  # accent preserved
    assert lines[-1] == "Zoe Smith"


def test_reports_directory_instead_of_file(working_directory, capsys):
    some_dir = working_directory / "a-folder"
    some_dir.mkdir()

    exit_code = main([str(some_dir)])

    assert exit_code == EXIT_MISSING_FILE
    assert "directory" in capsys.readouterr().err


def test_reports_non_utf8_file(working_directory, capsys):
    binary_file = working_directory / "binary.txt"
    binary_file.write_bytes(b"\xff\xfe\x00\x00invalid")

    exit_code = main([str(binary_file)])

    assert exit_code == EXIT_MISSING_FILE
    assert "UTF-8" in capsys.readouterr().err
