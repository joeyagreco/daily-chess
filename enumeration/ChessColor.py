from __future__ import annotations

from enum import unique

from enumeration.BaseEnum import BaseEnum


@unique
class ChessColor(BaseEnum):
    BLACK = "BLACK"
    WHITE = "WHITE"

    @staticmethod
    def items() -> list[tuple[ChessColor, str]]:
        return [(member, member.name) for member in ChessColor]

    @classmethod
    def from_str(cls, s: str) -> ChessColor:
        for member, _ in ChessColor.items():
            if member.value.upper() == s.upper():
                return member
        raise ValueError(f"'{s}' is not a valid ChessColor.")
