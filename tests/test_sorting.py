from name_sorter.parsing import parse_name
from name_sorter.sorting import sort_names
from tests.conftest import BRIEF_EXAMPLE_INPUT, BRIEF_EXAMPLE_OUTPUT


def _sorted_text(lines):
    names = [parse_name(line) for line in lines]
    return [str(name) for name in sort_names(names)]


def test_sorts_the_example_from_the_brief():
    assert _sorted_text(BRIEF_EXAMPLE_INPUT) == BRIEF_EXAMPLE_OUTPUT


def test_breaks_last_name_ties_with_given_names():
    assert _sorted_text(["Zoe Smith", "Adam Smith"]) == ["Adam Smith", "Zoe Smith"]


def test_shorter_name_sorts_before_longer_shared_prefix():
    assert _sorted_text(["Beau Tristan Bentley", "Beau Bentley"]) == [
        "Beau Bentley",
        "Beau Tristan Bentley",
    ]


def test_sort_is_case_insensitive():
    assert _sorted_text(["beau bentley", "Marin Alvarez"]) == [
        "Marin Alvarez",
        "beau bentley",
    ]


def test_duplicates_are_preserved():
    assert _sorted_text(["Leo Gardner", "Leo Gardner"]) == [
        "Leo Gardner",
        "Leo Gardner",
    ]


def test_given_names_break_ties_when_surnames_differ_only_by_case():
    assert _sorted_text(["Zoe smith", "Adam Smith"]) == [
        "Adam Smith",
        "Zoe smith",
    ]


def test_sorts_an_empty_list():
    assert sort_names([]) == []
