from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from enumeration.ChessGameOutcome import ChessGameOutcome
from enumeration.ChessGameTermination import ChessGameTermination


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
    termination: ChessGameTermination
    moves: str
    opening_name: Optional[str] = None

    @property
    def derived_termination(self) -> ChessGameTermination:
        """
        Gives a more accurate termination than what Lichess provides.
        Adds endings like "Checkmate" or "Resignation".
        """
        termination = self.termination
        # check if this was a checkmate
        if "wins by checkmate" in self.moves:
            termination = ChessGameTermination.CHECKMATE

        if self.result == "1/2-1/2" and termination in (
            ChessGameTermination.NORMAL,
            ChessGameTermination.TIME_FORFEIT,
        ):
            # draw, normal outcome
            # only options (i think) are insufficient material, 50 moves, threefold repetition, and stalemate
            if "Draw by stalemate" in self.moves:
                termination = ChessGameTermination.STALEMATE
            elif "Draw by time and insufficient material" in self.moves:
                termination = ChessGameTermination.INSUFFICIENT_MATERIAL
            # NOTE: do not have example API data for some outcomes, so they are not added yet
            # NOTE: no support for 50 moves yet
            # NOTE: no support for threefold repetition yet
        elif self.result != "1/2-1/2" and termination == ChessGameTermination.NORMAL:
            # non-draw, normal outcome
            # only option (i think) is resignation
            termination = ChessGameTermination.RESIGNATION
        return termination

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

    @property
    def loser_username(self) -> Optional[str]:
        """
        Returns None for draws.
        """
        loser_username = None
        if self.result == "1-0":
            loser_username = self.black_username
        elif self.result == "0-1":
            loser_username = self.white_username
        return loser_username

    @property
    def winner_elo(self) -> Optional[int]:
        """
        Returns the elo for the game winner.
        Returns None for draws.
        """
        winner_elo = None
        if self.result == "1-0":
            winner_elo = self.white_elo
        elif self.result == "0-1":
            winner_elo = self.black_elo
        return winner_elo

    @property
    def loser_elo(self) -> Optional[int]:
        """
        Returns the elo for the game loser.
        Returns None for draws.
        """
        loser_elo = None
        if self.result == "1-0":
            loser_elo = self.black_elo
        elif self.result == "0-1":
            loser_elo = self.white_elo
        return loser_elo

    def elo_change_for_user(self, username: str) -> int:
        """
        Returns the elo difference from this game for the given username.
        """
        if username == self.white_username:
            return int(self.white_rating_dif)
        elif username == self.black_username:
            return int(self.black_rating_dif)

        raise Exception(f"Invalid username '{username}' for game.")

    def elo_for_user(self, username: str, *, after_game: bool = False) -> int:
        """
        Returns the elo at the time of this game for the given username.
        """
        if username == self.white_username:
            elo = int(self.white_elo)
            if after_game:
                elo += self.elo_change_for_user(username)
            return elo
        elif username == self.black_username:
            elo = int(self.black_elo)
            if after_game:
                elo += self.elo_change_for_user(username)
            return elo

        raise Exception(f"Invalid username '{username}' for game.")

    def outcome_for_user(self, username: str) -> ChessGameOutcome:
        """
        Returns the outcome of this game for the given username..
        """
        if username not in (self.white_username, self.black_username):
            raise Exception(f"Invalid username '{username}' for game.")
        winner_username = self.winner_username
        outcome = ChessGameOutcome.TIE
        if winner_username is not None:
            outcome = ChessGameOutcome.WIN if winner_username == username else ChessGameOutcome.LOSS
        return outcome

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
            termination=ChessGameTermination.from_str(metadata["Termination"]),
            moves=moves,
        )
