# Name Sorter

Submission for the Dye & Durham coding assessment.

Sorts a list of names by last name, then by given names. Prints the result and writes it to a file.

## Quickstart

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest
name-sorter ./unsorted-names-list.txt
```

Python 3.11 or newer.

## What it does

Give it a file with one name per line:

```
Janet Parsons
Vaughn Lewis
Adonis Julius Archer
```

Run it:

```bash
name-sorter ./unsorted-names-list.txt
```

You get the sorted list on screen and in `sorted-names-list.txt`. Any rows that don't parse go to `rejected-names.txt` with the line number and reason.

Exit codes:
- 0: everything parsed and sorted cleanly
- 1: some rows were rejected, the valid ones were still sorted and written
- 2: something broke before parsing (missing file, directory instead of file, non-UTF-8 input)

## How the pieces fit

Each file does one thing:

- `name.py`: what a Name is, how two Names compare
- `parsing.py`: turn a line of text into a Name, or a Reject if it won't parse
- `sorting.py`: order a list of Names
- `io_adapters.py`: read from a file, write to stdout, write to a file
- `rejects.py`: write the rejects report
- `app.py`: the use case, read parse sort write
- `cli.py`: argument parsing and exit codes

The use case talks to I/O through Protocols, not through concrete file classes. The CLI is the only part that constructs the real file-backed source and sinks and passes them in. That keeps the use case testable without touching the disk.

## Design decisions worth calling out

A Name validates itself when you construct it. If you're holding a Name, it's valid. Nothing downstream has to re-check.

The sort rule lives on the Name as a `sort_key` property. The sort function is a one-line wrapper around `sorted()`. If the sort rule changes, I touch one property.

Output goes to two places (stdout and the file). The CLI wraps them in a composite sink that implements the same Protocol as the individual sinks.

The sort key normalizes Unicode (NFKD, strip combining marks, casefold) so José sorts with Jose rather than being banished to the end of the alphabet by Unicode code point. The displayed name is always the original, untouched. Normalization is for comparison, never for display.

Invalid rows don't abort the run. Valid rows still get sorted and written. Invalid rows go to `rejected-names.txt` with the line number and reason. If 997 of 1000 rows are valid, the user still gets 997 sorted names plus a report of the 3 bad ones. Exit code 1 tells automation something was rejected.

More rationale in `DESIGN.md`.

## Assumptions

The brief leaves some things open. Here's what I decided:

- Empty input file: produce an empty output file, exit 0.
- Blank lines in input: skipped.
- Leading and trailing whitespace: trimmed before parsing.
- Case: ignored for sorting (beau and Beau sort together), preserved in output.
- Accented letters: normalized for comparison (José sorts with Jose), preserved in output.
- Duplicate names: preserved.
- Digits and symbols in a name part: accepted. The brief defines validity structurally, not by character class, and any character filter risks rejecting someone's legitimate name.
- Mononyms (single-word legal names like Madonna or Plato): rejected, because the brief requires at least one given name. Noted as a known real-world limitation.
- Non-Latin scripts (Cyrillic, CJK, Arabic, Hebrew): sort by Unicode code point block. Each script groups together. Not locale-correct, but deterministic. Locale-aware collation (Swedish ä after z, traditional Spanish ñ between n and o) would need pyicu or Python's locale module, and "whose locale" is a decision for the data owner.
- Western name order assumed. Input like "李 明" would be parsed with 明 as the surname, which is wrong for Chinese convention. The brief's examples are all Western, so I didn't try to handle the reversed order.

## Tests

```bash
pytest
```

Tests cover each module in isolation, the full CLI end to end, the exact example from the brief, and a 1000-name case (which the brief says will be used for grading). There are also tests for the error paths (missing file, directory instead of a file, non-UTF-8 input, mixed valid and invalid rows).

## CI

GitHub Actions runs the test suite and a smoke test on every push and pull request. See `.github/workflows/ci.yml`. The smoke test runs `name-sorter ./unsorted-names-list.txt` against the exact example from the brief and verifies output.

## If I were taking this further

- Replace the lambda in sort_names with a named function if more sort configurations get added.
- Collect multiple parse errors into a nicer summary format.
- Handle PermissionError explicitly in the CLI.
- Locale-aware collation for non-Latin scripts via pyicu.
- Benchmark against a very large input (millions of names) and switch to streaming if memory becomes a concern.
- Integration tests that run the compiled binary against fixture files, not just via `main()`.