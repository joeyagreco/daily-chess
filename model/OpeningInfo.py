from dataclasses import dataclass

from enumeration.ChessColor import ChessColor
from enumeration.ChessGameOutcome import ChessGameOutcome
from model.ChessOpening import ChessOpening


@dataclass(kw_only=True)
class OpeningInfo:
    net_elo: int
    chess_opening: ChessOpening
    player_color: ChessColor
    player_outcomes: list[ChessGameOutcome]
