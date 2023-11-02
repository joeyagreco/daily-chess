from __future__ import annotations

from enum import unique

from enumeration.BaseEnum import BaseEnum


@unique
class Sort(BaseEnum):
    DATE_ASC = "dateAsc"
    DATE_DESC = "dateDesc"

    @staticmethod
    def items() -> list[tuple[Sort, str]]:
        return [(member, member.name) for member in Sort]

    @classmethod
    def from_str(cls, s: str) -> Sort:
        s_upper = s.upper()
        for member, member_name in Sort.items():
            if member_name == s_upper:
                return member
        raise ValueError(f"'{s}' is not a valid Sort.")
