from __future__ import annotations

from dataclasses import dataclass

from model.abstract.DictDeserializable import DictDeserializable
from model.ChessPlayer import ChessPlayer


@dataclass(kw_only=True)
class ChessPlayers(DictDeserializable):
    white: ChessPlayer
    black: ChessPlayer

    @staticmethod
    def from_dict(d: dict) -> ChessPlayers:
        return ChessPlayers(
            white=ChessPlayer.from_dict(d["white"]), black=ChessPlayer.from_dict(d["black"])
        )
