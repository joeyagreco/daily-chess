from __future__ import annotations

from dataclasses import dataclass

from model.abstract.DictDeserializable import DictDeserializable


@dataclass(kw_only=True)
class ChessOpening(DictDeserializable):
    eco: str
    name: str
    ply: int

    @staticmethod
    def from_dict(d: dict) -> ChessOpening:
        return ChessOpening(eco=d["eco"], name=d["name"], ply=d["ply"])
