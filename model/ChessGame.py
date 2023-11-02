from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


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
    termination: str
    moves: str
    opening_name: Optional[str] = None

    @property
    def winner_username(self) -> Optional[str]:
        """
        Returns None for draws.
        """
        winner_username = None
        if self.result == "1-0":
            winner_username = self.white_username
        elif self.result == "0-1":
            winner_username = self.black_username
        return winner_username

    def from_text(text: str) -> ChessGame:
        metadata = {key: value for key, value in re.findall(r'\[(.*?) "(.*?)"\]', text)}
        moves = re.search(r"\n\n(.*?)$", text, re.DOTALL).group(1)

        return ChessGame(
            event_name=metadata["Event"],
            game_url=metadata["Site"],
            date=datetime.strptime(metadata["Date"], "%Y.%m.%d").date(),
            white_username=metadata["White"],
            black_username=metadata["Black"],
            result=metadata["Result"],
            utc_date=datetime.strptime(metadata["UTCDate"], "%Y.%m.%d").date(),
            white_elo=metadata["WhiteElo"],
            black_elo=metadata["BlackElo"],
            white_rating_dif=metadata["WhiteRatingDiff"],
            black_rating_dif=metadata["BlackRatingDiff"],
            variant=metadata["Variant"],
            time_control=metadata["TimeControl"],
            opening_name=metadata.get("Opening"),
            termination=metadata["Termination"],
            moves=moves,
        )
