from __future__ import annotations

from enum import unique

from enumeration.BaseEnum import BaseEnum


@unique
class ChessGameTermination(BaseEnum):
    CHECKMATE = "CHECKMATE"
    # FIFTY_MOVES = "FIFTY MOVES"  # NOTE: not yet supported in logic
    INSUFFICIENT_MATERIAL = "INSUFFICIENT MATERIAL"
    NORMAL = "NORMAL"
    RESIGNATION = "RESIGNATION"
    STALEMATE = "STALEMATE"
    # THREEFOLD_REPETITION = "THREEFOLD REPETITION"  # NOTE: not yet supported in logic
    TIME_FORFEIT = "TIME FORFEIT"

    @staticmethod
    def items() -> list[tuple[ChessGameTermination, str]]:
        return [(member, member.value) for member in ChessGameTermination]

    @classmethod
    def from_str(cls, s: str) -> ChessGameTermination:
        for member, _ in ChessGameTermination.items():
            if member.value.upper() == s.upper():
                return member
        raise ValueError(f"'{s}' is not a valid ChessGameTermination.")
