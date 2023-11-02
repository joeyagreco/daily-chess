from collections import defaultdict

from enumeration.PerfType import PerfType
from enumeration.Sort import Sort
from model.ChessGame import ChessGame
from service.chess_game import get_games_for_user
from util.discord import send_webhook
from util.EnvironmentReader import EnvironmentReader

if __name__ == "__main__":
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

    # filter out to include games that were lost and tied
    # loss = 1
    # tie = 0.5
    openings_and_negative_count = defaultdict(float)
    openings_and_game_urls: dict[str, list[str]] = {}
    for game in games:
        if game.opening_name not in openings_and_game_urls.keys():
            openings_and_game_urls[game.opening_name] = []
        openings_and_game_urls[game.opening_name].append(game.game_url)
        if game.result == "0-1":
            openings_and_negative_count[game.opening_name] += 1
        elif game.result == "1/2-1/2":
            openings_and_negative_count[game.opening_name] += 0.5
    openings_and_negative_count = dict(openings_and_negative_count)

    # Convert dict to sorted list of tuples
    sorted_openings = sorted(openings_and_negative_count.items(), key=lambda x: x[1], reverse=True)

    send_openings = sorted_openings[: DISCORD_DAILY_OPENINGS_TO_SEND + 1]
    for opening_name, _ in send_openings:
        ...

    # send to discord
    print("1")
    send_webhook(webhook_url=WEBHOOK_URL, content=str(openings_and_game_urls))
    print("2")
