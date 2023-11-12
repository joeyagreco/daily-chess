from typing import Optional

from api.LichessApiClient import LichessApiClient
from enumeration.PerfType import PerfType
from enumeration.Sort import Sort
from model.ChessGameV2 import ChessGameV2


def get_games_for_user_v2(
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
    last_fen: Optional[bool] = None
) -> list[ChessGameV2]:
    lichess_api_client = LichessApiClient()
    return lichess_api_client.get_games_for_user_v2(
        username,
        max=max,
        rated=rated,
        perf_type=perf_type,
        tags=tags,
        sort=sort,
        opening=opening,
        finished=finished,
        literate=literate,
        last_fen=last_fen,
    )
