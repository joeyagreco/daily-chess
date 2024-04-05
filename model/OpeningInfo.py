from dataclasses import dataclass

from enumeration.ChessColor import ChessColor
from enumeration.ChessGameOutcome import ChessGameOutcome


@dataclass(kw_only=True)
class OpeningInfo:
    net_elo: int
    opening_name: str
    player_color: ChessColor
    player_outcomes: list[ChessGameOutcome]
