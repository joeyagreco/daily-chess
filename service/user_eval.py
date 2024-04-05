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
                "opening_name": game.opening.name,
                "player_color": user_color,
                "net_rating": rating_diff,
                "player_outcomes": [player_outcome],
            } 
            
    
    opening_infos = []
    
    for tracked_info in info_tracking.values():
        opening_infos.append(
            OpeningInfo(
                net_elo=tracked_info["net_rating"],
                opening_name=tracked_info["opening_name"],
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

def get_elo_string(elo: int) -> str:
    modifier = ""
    if elo > 0:
        modifier = "+"
    return f"{modifier}{elo}"

def get_emoji_for_elo(elo: int) -> str:
    emoji = ":chart_with_upwards_trend:" if elo > 0 else ":chart_with_downwards_trend:"
    return ":heavy_minus_sign:" if elo == 0 else emoji

def get_emoji_for_color(color: ChessColor) -> str:
    if color == ChessColor.WHITE:
        return ":white_large_square:"
    return ":black_large_square:"


# def get_sorted_opening_infos(opening_infos: list[OpeningInfo], *, worst_elo_first: bool = True) -> list[OpeningInfo]:
#     return sorted(opening_infos, key=lambda opening: opening.net_elo)
