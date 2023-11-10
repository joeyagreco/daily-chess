import json
from typing import Optional

import requests

from api.BaseApiClient import BaseApiClient
from enumeration.PerfType import PerfType
from enumeration.Sort import Sort
from model.ChessGame import ChessGame
from model.ChessGameV2 import ChessGameV2


class LichessApiClient(BaseApiClient):
    __BASE_URL = "https://lichess.org/api"
    __GAMES_ROUTE = "/games"
    __USER_ROUTE = "/user"

    def __init__(self):
        super().__init__()

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
        literate: Optional[bool] = None,
    ) -> list[ChessGame]:
        ...
        url = f"{cls.__BASE_URL}{cls.__GAMES_ROUTE}{cls.__USER_ROUTE}/{username}"

        params = {}
        if max is not None:
            params["max"] = max
        if rated is not None:
            params["rated"] = rated
        if perfType is not None:
            params["perfType"] = perfType.value
        if tags is not None:
            params["tags"] = tags
        if sort is not None:
            params["sort"] = sort.value
        if opening is not None:
            params["opening"] = opening
        if finished is not None:
            params["finished"] = finished
        if literate is not None:
            params["literate"] = literate

        url = cls._build_url_with_params(url, params)

        response = cls._rest_call(requests.get, url)

        games_list = []
        games_text = response.text.strip().split("\n\n\n")
        for game_text in games_text:
            games_list.append(ChessGame.from_text(game_text))
        return games_list

    @classmethod
    def get_games_for_user_v2(
        cls,
        username: str,
        *,
        max: Optional[int] = None,
        rated: Optional[bool] = None,
        perf_type: Optional[PerfType] = None,
        tags: Optional[bool] = None,
        sort: Optional[Sort] = None,
        opening: Optional[bool] = None,
        finished: Optional[bool] = None,
        literate: Optional[bool] = None,
        last_fen: Optional[bool] = None,
    ) -> list[ChessGameV2]:
        headers = {"Accept": "application/x-ndjson"}

        url = f"{cls.__BASE_URL}{cls.__GAMES_ROUTE}{cls.__USER_ROUTE}/{username}"

        params = {}
        if max is not None:
            params["max"] = max
        if rated is not None:
            params["rated"] = rated
        if perf_type is not None:
            params["perfType"] = perf_type.value
        if tags is not None:
            params["tags"] = tags
        if sort is not None:
            params["sort"] = sort.value
        if opening is not None:
            params["opening"] = opening
        if finished is not None:
            params["finished"] = finished
        if literate is not None:
            params["literate"] = literate
        if last_fen is not None:
            params["lastFen"] = last_fen

        url = cls._build_url_with_params(url, params)

        response = cls._rest_call(requests.get, url, headers=headers)

        # need this instead of .json for application/x-ndjson response
        data = [json.loads(line) for line in response.iter_lines(decode_unicode=True) if line]

        games_list = []
        for game in data:
            games_list.append(ChessGameV2.from_dict(game))
        return games_list
