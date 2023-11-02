from __future__ import annotations

from enum import unique

from enumeration.BaseEnum import BaseEnum


@unique
class PerfType(BaseEnum):
    ANTICHESS = "antichess"
    ATOMIC = "atomic"
    BLITZ = "blitz"
    BULLET = "bullet"
    CHESS_960 = "chess960"
    CLASSICAL = "classical"
    CORRESPONDENCE = "correspondence"
    CRAZYHOUSE = "crazyhouse"
    KING_OF_THE_HILL = "kingOfTheHill"
    RACING_KINGS = "racingKings"
    RAPID = "rapid"
    THREE_CHECK = "threeCheck"
    ULTRA_BULLET = "ultraBullet"

    @staticmethod
    def items() -> list[tuple[PerfType, str]]:
        return [(member, member.name) for member in PerfType]

    @classmethod
    def from_str(cls, s: str) -> PerfType:
        s_upper = s.upper()
        for member, member_name in PerfType.items():
            if member_name == s_upper:
                return member
        raise ValueError(f"'{s}' is not a valid PerfType.")
