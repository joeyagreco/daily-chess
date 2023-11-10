import time
from collections import defaultdict

import schedule

from enumeration.ChessGameOutcome import ChessGameOutcome
from enumeration.ChessStatus import ChessStatus
from enumeration.HexColor import HexColor
from enumeration.PerfType import PerfType
from enumeration.Sort import Sort
from model.ChessGameV2 import ChessGameV2
from service.chess_game import get_games_for_user_v2
from util.discord import send_discord_message
from util.EnvironmentReader import EnvironmentReader

USERNAME = EnvironmentReader.get("LICHESS_USERNAME")
NUM_GAMES = int(EnvironmentReader.get("NUM_GAMES"))
PERF_TYPE = PerfType.from_str(EnvironmentReader.get("PERF_TYPE"))
WEBHOOK_URL = EnvironmentReader.get("DISCORD_WEBHOOK_URL")
DISCORD_DAILY_OPENINGS_TO_SEND = int(EnvironmentReader.get("DISCORD_DAILY_OPENINGS_TO_SEND"))


def main() -> None:
    games: list[ChessGameV2] = get_games_for_user_v2(
        USERNAME,
        max=NUM_GAMES,
        rated=True,
        perf_type=PERF_TYPE,
        tags=True,
        sort=Sort.DATE_DESC,
        opening=True,
        finished=True,
        literate=True,
        last_fen=True,
    )

    # calculate net elo for each opening
    openings_and_net_elo = defaultdict(float)

    # calculate best and worst user/elo beat and lost to
    highest_elo_beat = None
    lowest_elo_lost = None
    highest_elo_beat_username = None
    lowest_elo_lost_username = None

    # keep track of each game's outcome (status)
    status_and_count = {}
    for _, status in ChessStatus.items():
        status_and_count[status] = {}
        for _, outcome in ChessGameOutcome.items():
            status_and_count[status][outcome] = 0

    # holds urls, game outcome
    openings_and_game_info: dict[str, list[dict]] = {}
    for game in games:
        if game.opening.name not in openings_and_game_info.keys():
            openings_and_game_info[game.opening.name] = []
        openings_and_net_elo[game.opening.name] += game.get_chess_player(USERNAME).rating_diff

        # get game outcome (status)
        game_outcome = game.outcome_for_user(USERNAME)
        status_and_count[game.status.value][game_outcome.value] += 1

        # calculate best win / worst loss
        if game_outcome != ChessGameOutcome.TIE:
            winner_elo = game.winning_player.rating
            loser_elo = game.losing_player.rating

            if game_outcome == ChessGameOutcome.WIN and (
                highest_elo_beat is None or loser_elo > highest_elo_beat
            ):
                highest_elo_beat = loser_elo
                highest_elo_beat_username = game.losing_player.user.name
            elif game_outcome == ChessGameOutcome.LOSS and (
                lowest_elo_lost is None or winner_elo < lowest_elo_lost
            ):
                lowest_elo_lost = winner_elo
                lowest_elo_lost_username = game.winning_player.user.name

        openings_and_game_info[game.opening.name].append(
            {"url": game.game_url, "outcome": game_outcome.value, "status": game.status.value}
        )
        # sort
        # primary sort on: win -> loss -> tie
        # secondary sort on: status
        openings_and_game_info[game.opening.name].sort(
            key=lambda x: ({"WIN": 0, "LOSS": 1, "TIE": 2}[x["outcome"]], x["status"])
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
            value += f"[{game_info['outcome']} ({game_info['status']})]({game_info['url']})\n"
        fields.append({"name": opening_name, "value": value, "inline": True})

    # sort from most -> least frequent openings
    opening_and_frequency_embeds = sorted(
        opening_and_frequency_embeds, key=lambda x: int(x["value"]), reverse=True
    )

    status_embed_fields = []
    # create embeds for each game outcome type (status)
    for status, outcomes in status_and_count.items():
        # ensure that there was at least 1 game with this status before adding it
        if (
            outcomes[ChessGameOutcome.WIN.value]
            + outcomes[ChessGameOutcome.LOSS.value]
            + outcomes[ChessGameOutcome.TIE.value]
            > 0
        ):
            status_embed_fields.append(
                {
                    "name": status,
                    "value": f"{outcomes[ChessGameOutcome.WIN.value]}-{outcomes[ChessGameOutcome.LOSS.value]}-{outcomes[ChessGameOutcome.TIE.value]}",
                    "inline": False,
                }
            )

    # sort embeds from most -> least games
    status_embed_fields.sort(key=lambda x: sum(int(v) for v in x["value"].split("-")), reverse=True)

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

    terminations_embed = {
        "description": "Record By Outcome",
        "fields": status_embed_fields,
        "color": HexColor.TEAL.value,
    }

    # calculate elo change
    starting_elo = games[-1].get_chess_player(USERNAME).rating
    ending_elo = games[0].get_chess_player(USERNAME).rating_after_game
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
            terminations_embed,
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
            try:
                schedule.run_pending()
                time.sleep(1)
            except Exception as e:
                send_discord_message(
                    webhook_url=WEBHOOK_URL,
                    embeds=[{"title": "ERROR", "description": e, "color": HexColor.RED.value}],
                )
