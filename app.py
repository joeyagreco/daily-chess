from api.LichessApiClient import LichessApiClient
from enumeration.PerfType import PerfType
from enumeration.Sort import Sort

if __name__ == "__main__":
    lac = LichessApiClient()
    games = lac.get_games_for_user(
        "drcoffeekill",
        max=2,
        rated=True,
        perfType=PerfType.BLITZ,
        tags=True,
        sort=Sort.DATE_DESC,
        opening=True,
        finished=True,
    )
    print(games[0])
