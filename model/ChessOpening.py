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

    @staticmethod
    def get_lichess_url(opening_name: str) -> str:
        normalized_opening_name = opening_name
        replacers = {" ": "_", ":": ""}
        for k, v in replacers.items():
            normalized_opening_name = normalized_opening_name.replace(k, v)
        return f"https://lichess.org/opening/{normalized_opening_name}"
