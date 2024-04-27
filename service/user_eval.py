from datetime import datetime
from typing import Optional

from enumeration.ChessColor import ChessColor
from enumeration.ChessGameOutcome import ChessGameOutcome
from model.ChessGameV2 import ChessGameV2
from model.ChessPlayer import ChessPlayer
from model.OpeningInfo import OpeningInfo


def get_opening_infos(*, games: list[ChessGameV2], for_username: str) -> list[OpeningInfo]:
    info_tracking: dict[str, dict] = {}

    for game in games:
        player_outcome: ChessGameOutcome = game.outcome_for_user(for_username)
        player: ChessPlayer = game.get_chess_player(for_username)
        rating_diff: int = player.rating_diff
        user_color: ChessColor = game.color_for_user(for_username)

        key = f"{game.opening.name}{user_color.name}"

        if key in info_tracking:
            info_tracking[key]["net_rating"] += rating_diff
            info_tracking[key]["player_outcomes"].append(player_outcome)
        else:
            info_tracking[key] = {
                "chess_opening": game.opening,
                "player_color": user_color,
                "net_rating": rating_diff,
                "player_outcomes": [player_outcome],
            }

    opening_infos = []

    for tracked_info in info_tracking.values():
        opening_infos.append(
            OpeningInfo(
                net_elo=tracked_info["net_rating"],
                chess_opening=tracked_info["chess_opening"],
                player_color=tracked_info["player_color"],
                player_outcomes=tracked_info["player_outcomes"],
            )
        )

    return opening_infos


def get_record_string(outcomes: list[ChessGameOutcome]) -> str:
    losses = 0
    ties = 0
    wins = 0
    for outcome in outcomes:
        if outcome == ChessGameOutcome.LOSS:
            losses += 1
        elif outcome == ChessGameOutcome.TIE:
            ties += 1
        else:
            wins += 1
    return f"{wins}-{losses}-{ties}"


def get_elo_string(elo: float) -> str:
    rounded_elo = round(elo, 2)
    modifier = ""
    if rounded_elo > 0:
        modifier = "+"
    return f"{modifier}{rounded_elo}"



def get_emoji_for_elo(elo: int) -> str:
    emoji = ":chart_with_upwards_trend:" if elo > 0 else ":chart_with_downwards_trend:"
    return ":heavy_minus_sign:" if elo == 0 else emoji


def get_emoji_for_color(color: ChessColor) -> str:
    if color == ChessColor.WHITE:
        return ":white_large_square:"
    return ":black_large_square:"


def get_current_date_as_string() -> str:
    return datetime.now().strftime("%A, %B %-d")


def get_games_with_opening(*, games: list[ChessGameV2], opening_name: str) -> list[ChessGameV2]:
    ret_games = []
    for game in games:
        if game.opening.name == opening_name:
            ret_games.append(game)
    return ret_games


def get_record_in_games(*, games: list[ChessGameV2], username: str) -> tuple[int, int, int]:
    """ Returns record as W-L-T """
    wins = 0
    losses = 0
    ties = 0
    for game in games:
        outcome = game.outcome_for_user(username)
        if outcome == ChessGameOutcome.WIN:
            wins += 1
        elif outcome == ChessGameOutcome.LOSS:
            losses += 1
        elif outcome == ChessGameOutcome.TIE:
            ties += 1
    return wins, losses, ties

def get_games_with_negative_rating_change(*, games: list[ChessGameV2], username: str, include_zero: bool = True) -> list[ChessGameV2]:
    ret_games = []
    for game in games:
        chess_player = game.get_chess_player(username)
        if chess_player.rating_diff < 0 or (include_zero and chess_player.rating_diff == 0):
            ret_games.append(game)
    return ret_games

def get_average_rating_change_in_games(*, games: list[ChessGameV2], username: str) -> int:
    total_rating_change = 0
    for g in games:
        total_rating_change += g.get_chess_player(username).rating_diff
    return total_rating_change / len(games)
            
