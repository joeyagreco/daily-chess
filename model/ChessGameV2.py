from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from enumeration.ChessColor import ChessColor
from enumeration.ChessGameOutcome import ChessGameOutcome
from enumeration.ChessStatus import ChessStatus
from model.abstract.DictDeserializable import DictDeserializable
from model.ChessClock import ChessClock
from model.ChessOpening import ChessOpening
from model.ChessPlayer import ChessPlayer
from model.ChessPlayers import ChessPlayers


@dataclass(kw_only=True)
class ChessGameV2(DictDeserializable):
    id: str
    rated: bool
    variant: str  # TODO: enum
    speed: str  # TODO: enum
    perf: str  # TODO: enum
    created_at: int
    last_move_at: int
    status: ChessStatus
    players: ChessPlayers
    winner: Optional[ChessColor]
    opening: ChessOpening
    moves: str
    clock: ChessClock
    last_fen: str

    @property
    def game_url(self) -> str:
        return f"https://lichess.org/{self.id}"

    @property
    def ended_in_draw(self) -> bool:
        return self.status in (ChessStatus.DRAW, ChessStatus.STALEMATE)

    @property
    def winning_player(self) -> Optional[ChessPlayer]:
        """
        Returns None for draws.
        """
        winning_player = None
        if not self.ended_in_draw:
            if self.winner == ChessColor.WHITE:
                winning_player = self.players.white
            elif self.winner == ChessColor.BLACK:
                winning_player = self.players.black
        return winning_player

    @property
    def losing_player(self) -> Optional[ChessPlayer]:
        """
        Returns None for draws.
        """
        losing_players = None
        if not self.ended_in_draw:
            if self.winner == ChessColor.WHITE:
                losing_players = self.players.black
            elif self.winner == ChessColor.BLACK:
                losing_players = self.players.white
        return losing_players

    def get_chess_player(self, username: str) -> ChessPlayer:
        if username not in (self.players.white.user.name, self.players.black.user.name):
            raise Exception(f"Invalid username '{username}' for game.")
        if self.players.white.user.name == username:
            return self.players.white
        else:
            return self.players.black

    def outcome_for_user(self, username: str) -> ChessGameOutcome:
        """
        Returns the outcome of this game for the given username..
        """
        if username not in (self.players.white.user.name, self.players.black.user.name):
            raise Exception(f"Invalid username '{username}' for game.")
        winning_player = self.winning_player
        outcome = ChessGameOutcome.TIE
        if winning_player is not None:
            outcome = (
                ChessGameOutcome.WIN
                if winning_player.user.name == username
                else ChessGameOutcome.LOSS
            )
        return outcome

    def color_for_user(self, username: str) -> ChessColor:
        """
        Returns the color of this game for the given username..
        """
        if username not in (self.players.white.user.name, self.players.black.user.name):
            raise Exception(f"Invalid username '{username}' for game.")
        color = ChessColor.WHITE
        if self.players.black.user.name == username:
            color = ChessColor.BLACK
        return color

    @staticmethod
    def from_dict(d: dict) -> ChessGameV2:
        winner = None
        if d.get("winner") is not None:
            winner = ChessColor.from_str(d["winner"])
        return ChessGameV2(
            id=d["id"],
            rated=bool(d["rated"]),
            variant=d["variant"],
            speed=d["speed"],
            perf=d["perf"],
            created_at=d["createdAt"],
            last_move_at=d["lastMoveAt"],
            status=ChessStatus.from_str(d["status"]),
            players=ChessPlayers.from_dict(d["players"]),
            winner=winner,
            opening=ChessOpening.from_dict(d["opening"]),
            moves=d["moves"],
            clock=ChessClock.from_dict(d["clock"]),
            last_fen=d["lastFen"],
        )
