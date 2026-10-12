import pytest

from name_sorter.name import InvalidNameError, Name


def test_str_puts_given_names_before_last_name():
    name = Name(given_names=("Adonis", "Julius"), last_name="Archer")
    assert str(name) == "Adonis Julius Archer"


def test_name_with_three_given_names_is_valid():
    name = Name(given_names=("Hunter", "Uriah", "Mathew"), last_name="Clarke")
    assert str(name) == "Hunter Uriah Mathew Clarke"


def test_name_requires_at_least_one_given_name():
    with pytest.raises(InvalidNameError, match="at least one"):
        Name(given_names=(), last_name="Parsons")


def test_name_rejects_four_given_names():
    with pytest.raises(InvalidNameError, match="at most 3"):
        Name(given_names=("A", "B", "C", "D"), last_name="Smith")


def test_name_requires_non_empty_last_name():
    with pytest.raises(InvalidNameError, match="last name"):
        Name(given_names=("Janet",), last_name="   ")


def test_sort_key_orders_by_last_name_first():
    assert Name(("Zoe",), "Alvarez").sort_key < Name(("Adam",), "Bentley").sort_key


def test_sort_key_is_case_insensitive():
    assert Name(("leo",), "gardner").sort_key < Name(("Leo",), "Harris").sort_key


def test_sort_key_treats_accented_letters_like_their_base():
    assert (
        Name(("Jose",), "Smith").sort_key[0][0]
        == Name(("Jose",), "Smith").sort_key[0][0]
    )
    assert Name(("edouard",), "Smith").sort_key < Name(("fred",), "Smith").sort_key
    assert Name(("Édouard",), "Smith").sort_key < Name(("Fred",), "Smith").sort_key


def test_sort_key_puts_shorter_name_before_longer_shared_prefix():
    shorter = Name(("Beau",), "Bentley")
    longer = Name(("Beau", "Tristan"), "Bentley")
    assert shorter.sort_key < longer.sort_key


def test_str_preserves_original_text_including_accents_and_scripts():
    """Normalization is for sorting; output keeps the original casing and marks."""
    assert str(Name(("José",), "Álvarez")) == "José Álvarez"
    assert str(Name(("Müller",), "Schmidt")) == "Müller Schmidt"
    assert str(Name(("明",), "李")) == "明 李"
    assert str(Name(("MARIN",), "ALVAREZ")) == "MARIN ALVAREZ"
