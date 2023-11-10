from typing import Optional

from api.LichessApiClient import LichessApiClient
from enumeration.PerfType import PerfType
from enumeration.Sort import Sort
from model.ChessGame import ChessGame


def get_games_for_user(
    username: str,
    *,
    max: Optional[int] = None,
    rated: Optional[bool] = None,
    perfType: Optional[PerfType] = None,
    tags: Optional[bool] = None,
    sort: Optional[Sort] = None,
    opening: Optional[bool] = None,
    finished: Optional[bool] = None,
    literate: Optional[bool] = None
) -> ChessGame:
    lichess_api_client = LichessApiClient()
    return lichess_api_client.get_games_for_user(
        username,
        max=max,
        rated=rated,
        perfType=perfType,
        tags=tags,
        sort=sort,
        opening=opening,
        finished=finished,
        literate=literate,
    )
