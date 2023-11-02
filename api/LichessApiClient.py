from typing import Optional

import requests

from api.BaseApiClient import BaseApiClient
from enumeration.PerfType import PerfType
from enumeration.Sort import Sort
from model.ChessGame import ChessGame


class LichessApiClient(BaseApiClient):
    __BASE_URL = "https://lichess.org/api"
    __GAMES_ROUTE = "/games"
    __USER_ROUTE = "/user"

    def __init__(self):
        pass

    @classmethod
    def get_games_for_user(
        cls,
        username: str,
        *,
        max: Optional[int] = None,
        rated: Optional[bool] = None,
        perfType: Optional[PerfType] = None,
        tags: Optional[bool] = None,
        sort: Optional[Sort] = None,
        opening: Optional[bool] = None,
        finished: Optional[bool] = None,
    ) -> list[ChessGame]:
        ...
        url = f"{cls.__BASE_URL}{cls.__GAMES_ROUTE}{cls.__USER_ROUTE}/{username}"

        params = {}
        if max is not None:
            params["max"] = max
        if rated is not None:
            params["rated"] = rated
        if perfType is not None:
            params["perfType"] = perfType.name
        if tags is not None:
            params["tags"] = tags
        if sort is not None:
            params["sort"] = sort.name
        if opening is not None:
            params["opening"] = opening
        if finished is not None:
            params["finished"] = finished

        url = cls._build_url_with_params(url, params)

        response = cls._rest_call(requests.get, url)

        games_list = []
        games_text = response.text.strip().split("\n\n\n")
        for game_text in games_text:
            games_list.append(ChessGame.from_text(game_text))
        return games_list
