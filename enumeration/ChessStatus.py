from __future__ import annotations

from enum import unique

from enumeration.BaseEnum import BaseEnum


@unique
class ChessStatus(BaseEnum):
    DRAW = "DRAW"
    MATE = "MATE"
    OUT_OF_TIME = "OUT_OF_TIME"
    RESIGN = "RESIGN"
    STALEMATE = "STALEMATE"
    TIMEOUT = "TIMEOUT"

    @staticmethod
    def items() -> list[tuple[ChessStatus, str]]:
        return [(member, member.name) for member in ChessStatus]

    @classmethod
    def from_str(cls, s: str) -> ChessStatus:
        for member, _ in ChessStatus.items():
            valid_strings = [member.value.upper(), member.value.upper().replace("_", "")]
            if s.upper() in valid_strings:
                return member
        raise ValueError(f"'{s}' is not a valid ChessStatus.")
