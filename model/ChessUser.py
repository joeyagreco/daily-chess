from __future__ import annotations

from dataclasses import dataclass

from model.abstract.DictDeserializable import DictDeserializable


@dataclass(kw_only=True)
class ChessUser(DictDeserializable):
    name: str
    id: str

    @staticmethod
    def from_dict(d: dict) -> ChessUser:
        return ChessUser(name=d["name"], id=d["id"])
