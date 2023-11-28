from __future__ import annotations

from enum import unique

from enumeration.BaseEnum import BaseEnum


@unique
class Color(BaseEnum):
    BLUE = "BLUE"
    GREEN = "GREEN"
    RED = "RED"

    @staticmethod
    def items() -> list[tuple[Color, str]]:
        return [(member, member.name) for member in Color]

    @classmethod
    def from_str(cls, s: str) -> Color:
        for member, _ in Color.items():
            valid_strings = [member.value.upper(), member.value.upper().replace("_", "")]
            if s.upper() in valid_strings:
                return member
        raise ValueError(f"'{s}' is not a valid Color.")
