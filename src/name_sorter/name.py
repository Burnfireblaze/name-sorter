from __future__ import annotations

import unicodedata
from dataclasses import dataclass

MAX_GIVEN_NAMES = 3


class InvalidNameError(ValueError):
    """Raised when text cannot be read as a valid name."""


def _normalize(part: str) -> str:
    decomposed = unicodedata.normalize("NFKD", part)
    without_accents = "".join(c for c in decomposed if not unicodedata.combining(c))
    return without_accents.casefold()


@dataclass(frozen=True, slots=True)
class Name:
    given_names: tuple[str, ...]
    last_name: str

    def __post_init__(self) -> None:
        if not self.last_name.strip():
            raise InvalidNameError("a name must have a last name")
        if not self.given_names:
            raise InvalidNameError(
                f"'{self.last_name}' has no given name; at least one is required"
            )
        if len(self.given_names) > MAX_GIVEN_NAMES:
            raise InvalidNameError(
                f"'{self}' has {len(self.given_names)} given names; "
                f"at most {MAX_GIVEN_NAMES} are allowed"
            )

    @property
    def sort_key(self) -> tuple:
        parts = (self.last_name, *self.given_names)
        normalized_parts = tuple(_normalize(part) for part in parts)
        return normalized_parts, parts

    def __str__(self) -> str:
        return " ".join((*self.given_names, self.last_name))
