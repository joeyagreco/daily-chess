from api.LichessApiClient import LichessApiClient

if __name__ == "__main__":
    lac = LichessApiClient()
    games = lac.get_games_for_user(
        "drcoffeekill",
        max=2,
        rated=True,
        perfType="blitz",
        tags=True,
        sort="dateDesc",
        opening=True,
        finished=True,
    )
    print(games[0])
