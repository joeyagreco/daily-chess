import time
from collections import defaultdict

import schedule

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
    RATED = bool(EnvironmentReader.get("RATED"))
    PERF_TYPE = PerfType.from_str(EnvironmentReader.get("PERF_TYPE"))
    WEBHOOK_URL = EnvironmentReader.get("DISCORD_WEBHOOK_URL")
    DISCORD_DAILY_OPENINGS_TO_SEND = int(EnvironmentReader.get("DISCORD_DAILY_OPENINGS_TO_SEND"))

    games: list[ChessGame] = get_games_for_user(
        USERNAME,
        max=NUM_GAMES,
        rated=RATED,
        perfType=PERF_TYPE,
        tags=True,
        sort=Sort.DATE_DESC,
        opening=True,
        finished=True,
    )

    # calculate net elo for each opening
    openings_and_net_elo = defaultdict(float)

    # holds urls, game outcome
    openings_and_game_info: dict[str, list[dict]] = {}
    for game in games:
        if game.opening_name not in openings_and_game_info.keys():
            openings_and_game_info[game.opening_name] = []
        openings_and_net_elo[game.opening_name] += game.elo_change_for_user(USERNAME)
        # if game.winner_username != USERNAME:
        game_outcome = "TIE"
        winner_username = game.winner_username
        if winner_username is not None:
            game_outcome = "WIN" if winner_username == USERNAME else "LOSS"

        openings_and_game_info[game.opening_name].append(
            {"url": game.game_url, "outcome": game_outcome}
        )
        # sort win -> tie -> loss
        openings_and_game_info[game.opening_name].sort(
            key=lambda x: {"WIN": 0, "TIE": 1, "LOSS": 2}[x["outcome"]]
        )
    openings_and_net_elo = dict(openings_and_net_elo)

    # Convert dict to sorted list of tuples
    sorted_openings = sorted(openings_and_net_elo.items(), key=lambda x: x[1], reverse=False)

    fields = []
    for opening_name, elo in sorted_openings:
        modifier = "+" if elo > 0 else ""
        value = f"\n({modifier}{elo} elo)\n\n"
        for game_info in openings_and_game_info[opening_name]:
            value += f"[{game_info['outcome']}]({game_info['url']})\n"
        fields.append({"name": opening_name, "value": value, "inline": False})

    worst_openings_embed = {
        "description": f"Your worst {DISCORD_DAILY_OPENINGS_TO_SEND} openings.",
        "fields": fields[:DISCORD_DAILY_OPENINGS_TO_SEND],
        "color": HexColor.RED.value,
    }

    best_openings_embed = {
        "description": f"Your best {DISCORD_DAILY_OPENINGS_TO_SEND} openings.",
        "fields": fields[::-1][:DISCORD_DAILY_OPENINGS_TO_SEND],
        "color": HexColor.GREEN.value,
    }

    # calculate elo change
    starting_elo = games[-1].elo_for_user(USERNAME)
    ending_elo = games[0].elo_for_user(USERNAME, after_game=True)
    elo_dif = str(ending_elo - starting_elo)
    # format elo dif
    elo_dif_color = HexColor.YELLOW.value
    if int(elo_dif) > 0:
        elo_dif = f"+{elo_dif}"
        elo_dif_color = HexColor.GREEN.value
    elif int(elo_dif) < 0:
        elo_dif_color = HexColor.RED.value

    fields = [
        {"name": "Starting Elo", "value": str(starting_elo), "inline": False},
        {"name": "Ending Elo", "value": str(ending_elo), "inline": False},
        {"name": "Elo Change", "value": elo_dif, "inline": False},
    ]
    elo_change_embed = {"description": f"Elo Recap", "fields": fields, "color": elo_dif_color}

    title_embed = {
        "title": "DAILY CHESS UPDATE",
        "description": f"Recap of your last {NUM_GAMES} games.",
        "color": HexColor.BLUE.value,
    }
    # send to discord
    send_discord_message(
        webhook_url=WEBHOOK_URL,
        embeds=[title_embed, worst_openings_embed, best_openings_embed, elo_change_embed],
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
