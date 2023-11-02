from api.LichessApiClient import LichessApiClient
from enumeration.PerfType import PerfType
from enumeration.Sort import Sort
from service.chess_game import get_games_for_user

if __name__ == "__main__":
    # lac = LichessApiClient()
    # games = lac.get_games_for_user(
    #     "drcoffeekill",
    #     max=2,
    #     rated=True,
    #     perfType=PerfType.BLITZ,
    #     tags=True,
    #     sort=Sort.DATE_DESC,
    #     opening=True,
    #     finished=True,
    # )
    # print(games[0])

    print(
        get_games_for_user(
            "drcoffeekill",
            max=2,
            rated=True,
            perfType=PerfType.BLITZ,
            tags=True,
            sort=Sort.DATE_DESC,
            opening=True,
            finished=True,
        )
    )
