# Design notes

Short record of the choices I made and why, so the next engineer (or me in six months) doesn't have to reverse-engineer them.

## Module boundaries

I split by reason-to-change, not by data flow. Each module should have one trigger for change.

| Module | Changes when |
|---|---|
| `name.py` | The definition of a valid name changes (e.g., allow 4 given names) |
| `parsing.py` | The input format changes (e.g., CSV, different separators) |
| `sorting.py` | The ordering rule changes (which in practice means `name.py`, since the sort key lives there) |
| `io_adapters.py` | I/O destinations change (new sources or sinks) |
| `rejects.py` | The reject-report format changes |
| `app.py` | The workflow changes (e.g., add a dedupe step between parse and sort) |
| `cli.py` | The command-line interface changes |

If a change forces me to edit two of these at once, one of them is in the wrong place.

## SOLID, where each one shows up

**Single Responsibility.** Each module has one reason to change (see table above). The clearest case is `Name`: it owns both the data and the validation. Separating validation into a `Validator` class would mean a validation-rule change touches two files instead of one.

**Open/Closed.** Adding a new I/O destination (JSON file, HTTP sink, database) means writing a new sink class, not editing an existing one. The composite sink is itself a sink, so the pattern composes.

**Liskov Substitution.** `StreamNameSink` and `FileNameSink` are interchangeable implementations of the `NameSink` protocol. Their underlying stream or file is an implementation detail; the use case treats them identically. Tests exercise this by passing a `StreamNameSink` backed by an `io.StringIO` in place of a `StreamNameSink` backed by `sys.stdout`.

**Interface Segregation.** `NameSource` has one method (`lines()`). `NameSink` has one method (`write()`). Separate interfaces so a class that only reads doesn't have to implement a `write()` it never calls.

**Dependency Inversion.** The use case (`app.py`) depends on the Protocols, not on `FileNameSource` and `FileNameSink`. The CLI constructs the concrete classes and injects them. Dependencies point inward toward the domain.

## Specific choices

### Validation on the Name itself

I put validation in `Name.__post_init__` instead of in a separate validator function. Reasons:

- A Name you're holding is a valid Name. No defensive checks downstream.
- Invariants are enforced in one place.
- If the rules change (allow 4 given names, add a middle-initial field), one file changes.

Downside: `Name` can't exist in an invalid state even temporarily, so building one with partial data isn't possible. For this problem that's fine.

### Protocols instead of ABCs

I used `typing.Protocol` for `NameSource` and `NameSink` rather than `abc.ABC` because:

- Structural typing lets tests pass in simple fakes without inheritance.
- No boilerplate for registering subclasses.
- Modern Python idiom.

If I needed runtime checks that a class implements the protocol, I could add `@runtime_checkable`. I didn't, because the use case doesn't do runtime type checks.

### The sort key as a tuple of tuples

Each sort key element is `(normalized_form, raw_form)`:

- The normalized form drives the ordering (José sorts with Jose).
- The raw form breaks ties deterministically (José vs Jose have the same normalized key, so the raw text decides).

Without the tie-breaker, José and Jose would compare equal and their output order would depend on input order.

### Composite sink for two destinations

The brief wants output on stdout and in a file. I could have called both from the CLI directly. Instead I made a `CompositeNameSink` that wraps multiple sinks and implements the same Protocol.

Reasons:
- The use case doesn't know there are two destinations.
- Adding a third destination (log sink, HTTP sink) means writing one new sink class, not editing the CLI.
- The composite is itself a sink, so the pattern composes naturally.

Tradeoff: slight over-engineering for two outputs. Worth it because it keeps the use case clean and makes the extension story obvious.

### Partial success instead of abort-on-error

If some rows don't parse, I still sort and write the valid ones. The rejects go to a separate file with line numbers and reasons. Exit code 1 tells automation something was rejected.

Reasons:
- A user with a 1000-row file and 3 bad lines gets 997 sorted names, instead of having to fix each error and re-run.
- The rejects file is persistent, easy to grep, diff, share. Better than terminal output alone.
- Matches how mature data-processing tools behave.

Alternative: abort on first error. Simpler but less friendly for larger inputs. I'd choose that for strict ETL pipelines where partial data is dangerous.

### Error handling in the CLI, not in lower layers

The CLI catches `FileNotFoundError`, `IsADirectoryError`, `UnicodeDecodeError`, and `OSError`. Each gets a user-friendly message prefixed with `name-sorter:`. Lower layers raise and let them bubble up.

Reasons:
- The CLI has context (program name, stderr, exit codes) that lower layers don't.
- Keeps error formatting in one place.
- If I ever embed the use case in a different frontend (library, web service), the error-translation layer swaps out, the use case doesn't change.

Order of except clauses matters: `FileNotFoundError`, `IsADirectoryError`, and `PermissionError` are all subclasses of `OSError`, so they must come before the generic `OSError` catch or they'd never fire.

## Edge case decisions

| Case | Behavior | Why |
|---|---|---|
| Empty file | Empty output, exit 0 | Empty input is valid input |
| Blank lines in input | Skipped | Text-file artifact, not data |
| Trailing/leading whitespace | Trimmed | Same reason |
| Mixed case | Case-insensitive sort, original preserved in output | Deterministic order without rewriting people's names |
| Unicode (José, Müller) | NFKD normalize + strip combining marks + casefold for comparison | Prevents accented letters from sorting to the end by code point |
| Non-Latin scripts | Sort by Unicode code point block | Deterministic without pyicu dependency |
| Duplicates | Preserved | Input is a list, not a set |
| Digits or symbols in names | Accepted | Brief defines validity structurally, not by character class |
| Mononyms (one word) | Rejected | Brief requires at least one given name |
| 4+ given names | Rejected | Brief allows at most 3 |
| Missing input file | Clear error on stderr, exit 2 | Standard Unix convention |