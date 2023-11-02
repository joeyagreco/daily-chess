from enumeration.PerfType import PerfType
from enumeration.Sort import Sort
from service.chess_game import get_games_for_user
from util.EnvironmentReader import EnvironmentReader

if __name__ == "__main__":
    NUMBER_OF_GAMES = 100
    USERNAME = EnvironmentReader.get("LICHESS_USERNAME")
    NUM_GAMES = int(EnvironmentReader.get("NUM_GAMES"))
    RATED = bool(EnvironmentReader.get("RATED"))
    PERF_TYPE = PerfType.from_str(EnvironmentReader.get("PERF_TYPE"))

    games = get_games_for_user(
        USERNAME,
        max=NUM_GAMES,
        rated=RATED,
        perfType=PERF_TYPE,
        tags=True,
        sort=Sort.DATE_DESC,
        opening=True,
        finished=True,
    )
