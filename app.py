import time
from collections import defaultdict

import schedule

from enumeration.ChessGameOutcome import ChessGameOutcome
from enumeration.HexColor import HexColor
from enumeration.PerfType import PerfType
from enumeration.Sort import Sort
from model.ChessGame import ChessGame
from service.chess_game import get_games_for_user
from util.discord import send_discord_message
from util.EnvironmentReader import EnvironmentReader


def main() -> None:
    USERNAME = EnvironmentReader.get("LICHESS_USERNAME")
    NUM_GAMES = int(EnvironmentReader.get("NUM_GAMES"))
    PERF_TYPE = PerfType.from_str(EnvironmentReader.get("PERF_TYPE"))
    WEBHOOK_URL = EnvironmentReader.get("DISCORD_WEBHOOK_URL")
    DISCORD_DAILY_OPENINGS_TO_SEND = int(EnvironmentReader.get("DISCORD_DAILY_OPENINGS_TO_SEND"))

    games: list[ChessGame] = get_games_for_user(
        USERNAME,
        max=NUM_GAMES,
        rated=True,
        perfType=PERF_TYPE,
        tags=True,
        sort=Sort.DATE_DESC,
        opening=True,
        finished=True,
    )

    # calculate net elo for each opening
    openings_and_net_elo = defaultdict(float)

    # calculate best and worst user/elo beat and lost to
    highest_elo_beat = None
    lowest_elo_lost = None
    highest_elo_beat_username = None
    lowest_elo_lost_username = None

    # holds urls, game outcome
    openings_and_game_info: dict[str, list[dict]] = {}
    for game in games:
        if game.opening_name not in openings_and_game_info.keys():
            openings_and_game_info[game.opening_name] = []
        openings_and_net_elo[game.opening_name] += game.elo_change_for_user(USERNAME)

        game_outcome = game.outcome_for_user(USERNAME)
        winner_elo = game.winner_elo
        loser_elo = game.loser_elo

        # calculate best win / worst loss
        if game_outcome == ChessGameOutcome.WIN and (
            highest_elo_beat is None or loser_elo > highest_elo_beat
        ):
            highest_elo_beat = loser_elo
            highest_elo_beat_username = game.loser_username
        elif game_outcome == ChessGameOutcome.LOSS and (
            lowest_elo_lost is None or winner_elo < lowest_elo_lost
        ):
            lowest_elo_lost = winner_elo
            lowest_elo_lost_username = game.winner_username

        openings_and_game_info[game.opening_name].append(
            {
                "url": game.game_url,
                "outcome": game_outcome.value,
                "termination": game.derived_termination.value,
            }
        )
        # sort
        # primary sort on: win -> loss -> tie
        # secondary sort on: checkmate -> resignation -> time forfeit
        openings_and_game_info[game.opening_name].sort(
            key=lambda x: (
                {"WIN": 0, "LOSS": 1, "TIE": 2}[x["outcome"]],
                {"CHECKMATE": 0, "RESIGNATION": 1, "TIME FORFEIT": 2}[x["termination"]],
            )
        )
    openings_and_net_elo = dict(openings_and_net_elo)

    # Convert dict to sorted list of tuples
    sorted_openings = sorted(openings_and_net_elo.items(), key=lambda x: x[1], reverse=False)

    # store all openings and the frequency
    opening_and_frequency_embeds = []

    fields = []
    for opening_name, elo in sorted_openings:
        outcome_counts = {
            outcome: sum(
                1 for game in openings_and_game_info[opening_name] if game["outcome"] == outcome
            )
            for outcome in ["WIN", "TIE", "LOSS"]
        }
        record_str = f"{outcome_counts['WIN']}-{outcome_counts['LOSS']}-{outcome_counts['TIE']}"
        pre_modifier = "+" if elo > 0 else ""
        emoji = ":chart_with_upwards_trend:" if elo > 0 else ":chart_with_downwards_trend:"
        emoji = ":heavy_minus_sign:" if elo == 0 else emoji
        value = f"\nELO: {pre_modifier}{elo} {emoji}\nGAMES PLAYED: {len(openings_and_game_info[opening_name])}\nRECORD: {record_str}\n\n"

        opening_and_frequency_embeds.append(
            {
                "name": opening_name,
                "value": str(len(openings_and_game_info[opening_name])),
                "inline": False,
            }
        )

        for game_info in openings_and_game_info[opening_name]:
            value += f"[{game_info['outcome']} ({game_info['termination']})]({game_info['url']})\n"
        fields.append({"name": opening_name, "value": value, "inline": True})

    # sort from most -> least frequent openings
    opening_and_frequency_embeds = sorted(
        opening_and_frequency_embeds, key=lambda x: int(x["value"]), reverse=True
    )

    worst_openings_embed = {
        "description": f"Worst {DISCORD_DAILY_OPENINGS_TO_SEND} openings",
        "fields": fields[:DISCORD_DAILY_OPENINGS_TO_SEND],
        "color": HexColor.RED.value,
    }

    best_openings_embed = {
        "description": f"Best {DISCORD_DAILY_OPENINGS_TO_SEND} openings",
        "fields": fields[::-1][:DISCORD_DAILY_OPENINGS_TO_SEND],
        "color": HexColor.GREEN.value,
    }

    most_played_openings_embed = {
        "description": f"Top {DISCORD_DAILY_OPENINGS_TO_SEND} most played openings",
        "fields": opening_and_frequency_embeds[:DISCORD_DAILY_OPENINGS_TO_SEND],
        "color": HexColor.LIGHT_BLUE.value,
    }

    best_win_and_worst_loss_embed = {
        "description": f"Best Win and Worst Loss",
        "fields": [
            {
                "name": "Best Win",
                "value": f"{highest_elo_beat_username}: {highest_elo_beat}",
                "inline": True,
            },
            {
                "name": "Worst Loss",
                "value": f"{lowest_elo_lost_username}: {lowest_elo_lost}",
                "inline": True,
            },
        ],
        "color": HexColor.PURPLE.value,
    }

    # calculate elo change
    starting_elo = games[-1].elo_for_user(USERNAME)
    ending_elo = games[0].elo_for_user(USERNAME, after_game=True)
    elo_dif = str(ending_elo - starting_elo)
    # format elo dif
    if int(elo_dif) > 0:
        elo_dif = f"+{elo_dif} :chart_with_upwards_trend:"
    elif int(elo_dif) < 0:
        elo_dif = f"{elo_dif} :chart_with_downwards_trend:"
    else:
        elo_dif = f"{elo_dif} :heavy_minus_sign:"

    elo_recap_fields = [
        {"name": "Starting Elo", "value": str(starting_elo), "inline": False},
        {"name": "Ending Elo", "value": str(ending_elo), "inline": False},
        {"name": "Elo Change", "value": elo_dif, "inline": False},
    ]

    title_embed = {
        "title": "DAILY CHESS UPDATE :chess_pawn:",
        "description": f"Recap of your last {NUM_GAMES} games.",
        "fields": elo_recap_fields,
        "color": HexColor.BLUE.value,
    }
    # send to discord
    send_discord_message(
        webhook_url=WEBHOOK_URL,
        embeds=[
            title_embed,
            best_win_and_worst_loss_embed,
            worst_openings_embed,
            best_openings_embed,
            most_played_openings_embed,
        ],
    )


if __name__ == "__main__":
    TEST = bool(EnvironmentReader.get("TEST"))
    if TEST:
        main()
    else:
        schedule.every().day.at(EnvironmentReader.get("RUN_AT_TIME")).do(main)

        while True:
            schedule.run_pending()
            time.sleep(1)
