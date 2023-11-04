from __future__ import annotations

from enum import unique

from enumeration.BaseEnum import BaseEnum


@unique
class HexColor(BaseEnum):
    BLACK = 0x000000
    BLUE = 0x0000FF
    DARK_RED = 0x8B0000
    GOLD = 0xFFD700
    GREEN = 0x00FF00
    LIGHT_BLUE = 0x6FBBD3
    ORANGE = 0xFFA500
    PURPLE = 0xA020F0
    RED = 0xFF0000
    TEAL = 0x008080
    WHITE = 0xFFFFFF
    YELLOW = 0xFFFF00

    @staticmethod
    def items() -> list[tuple[HexColor, str]]:
        return [(member, member.name) for member in HexColor]

    @classmethod
    def from_str(cls, s: str) -> HexColor:
        s_upper = s.upper()
        for member, member_name in HexColor.items():
            if member_name == s_upper:
                return member
        raise ValueError(f"'{s}' is not a valid HexColor.")
