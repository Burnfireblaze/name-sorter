import pytest


@pytest.fixture
def working_directory(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    return tmp_path


BRIEF_EXAMPLE_INPUT = [
    "Janet Parsons",
    "Vaughn Lewis",
    "Adonis Julius Archer",
    "Shelby Nathan Yoder",
    "Marin Alvarez",
    "London Lindsey",
    "Beau Tristan Bentley",
    "Leo Gardner",
    "Hunter Uriah Mathew Clarke",
    "Mikayla Lopez",
    "Frankie Conner Ritter",
]

BRIEF_EXAMPLE_OUTPUT = [
    "Marin Alvarez",
    "Adonis Julius Archer",
    "Beau Tristan Bentley",
    "Hunter Uriah Mathew Clarke",
    "Leo Gardner",
    "Vaughn Lewis",
    "London Lindsey",
    "Mikayla Lopez",
    "Janet Parsons",
    "Frankie Conner Ritter",
    "Shelby Nathan Yoder",
]
