from __future__ import annotations

from enum import unique

from enumeration.BaseEnum import BaseEnum


@unique
class ChessGameOutcome(BaseEnum):
    LOSS = "LOSS"
    TIE = "TIE"
    WIN = "WIN"

    @staticmethod
    def items() -> list[tuple[ChessGameOutcome, str]]:
        return [(member, member.name) for member in ChessGameOutcome]

    @classmethod
    def from_str(cls, s: str) -> ChessGameOutcome:
        s_upper = s.upper()
        for member, member_name in ChessGameOutcome.items():
            if member_name == s_upper:
                return member
        raise ValueError(f"'{s}' is not a valid ChessGameOutcome.")
