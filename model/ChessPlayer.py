from __future__ import annotations

from dataclasses import dataclass

from model.abstract.DictDeserializable import DictDeserializable
from model.ChessUser import ChessUser


@dataclass(kw_only=True)
class ChessPlayer(DictDeserializable):
    user: ChessUser
    rating: int
    rating_diff: int

    @property
    def rating_after_game(self) -> int:
        return self.rating + self.rating_diff

    @staticmethod
    def from_dict(d: dict) -> ChessPlayer:
        return ChessPlayer(
            user=ChessUser.from_dict(d["user"]), rating=d["rating"], rating_diff=d["ratingDiff"]
        )
