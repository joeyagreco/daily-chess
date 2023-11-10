from __future__ import annotations

from dataclasses import dataclass

from model.abstract.DictDeserializable import DictDeserializable


@dataclass(kw_only=True)
class ChessClock(DictDeserializable):
    initial: int
    increment: int
    total_time: int

    @staticmethod
    def from_dict(d: dict) -> ChessClock:
        return ChessClock(initial=d["initial"], increment=d["increment"], total_time=d["totalTime"])
