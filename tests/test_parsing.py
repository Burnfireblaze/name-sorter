from name_sorter.parsing import Reject, parse_lines, parse_name


def test_parses_a_single_name():
    name = parse_name("Marin Alvarez")
    assert name.given_names == ("Marin",)
    assert name.last_name == "Alvarez"


def test_parses_a_name_with_multiple_given_names():
    name = parse_name("Hunter Uriah Mathew Clarke")
    assert name.given_names == ("Hunter", "Uriah", "Mathew")
    assert name.last_name == "Clarke"


def test_parse_lines_skips_blank_lines():
    results = list(parse_lines(["", "Marin Alvarez", "   ", "Leo Gardner"]))
    assert len(results) == 2
    assert all(not isinstance(r, Reject) for r in results)


def test_parse_lines_yields_a_reject_for_invalid_input():
    results = list(parse_lines(["Marin Alvarez", "Smith"]))
    assert len(results) == 2
    assert isinstance(results[1], Reject)
    assert results[1].line_number == 2
    assert results[1].text == "Smith"


def test_parse_lines_yields_a_reject_for_too_many_given_names():
    results = list(parse_lines(["A B C D E Smith"]))
    assert isinstance(results[0], Reject)
    assert "at most 3" in results[0].reason
