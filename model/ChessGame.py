from __future__ import annotations

from dataclasses import dataclass


@dataclass(kw_only=True)
class ChessGame:
    event_name: str
    game_url: str
    date: date
    white_username: str
    black_username: str
    result: str
    utc_date: date
    white_elo: str
    black_elo: str
    white_rating_dif: str
    black_rating_dif: str
    variant: str
    time_control: str
    opening_name: str
    termination: str
    moves: str
