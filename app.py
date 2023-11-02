from collections import defaultdict

from enumeration.PerfType import PerfType
from enumeration.Sort import Sort
from model.ChessGame import ChessGame
from service.chess_game import get_games_for_user
from util.EnvironmentReader import EnvironmentReader

if __name__ == "__main__":
    USERNAME = EnvironmentReader.get("LICHESS_USERNAME")
    NUM_GAMES = int(EnvironmentReader.get("NUM_GAMES"))
    RATED = bool(EnvironmentReader.get("RATED"))
    PERF_TYPE = PerfType.from_str(EnvironmentReader.get("PERF_TYPE"))

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
    # loss = -1
    # tie = -0.5
    openings_and_negative_count = defaultdict(float)
    for game in games:
        if game.result == "0-1":
            openings_and_negative_count[game.opening_name] += 1
        elif game.result == "1/2-1/2":
            openings_and_negative_count[game.opening_name] += 0.5
    openings_and_negative_count = dict(openings_and_negative_count)
    print(openings_and_negative_count)
