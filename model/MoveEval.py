from dataclasses import dataclass
from typing import Optional


@dataclass(kw_only=True)
class MoveEval:
    actual_move: str
    eval_change: int
    fen_before_move: str
    engine_best_move: Optional[str] = None

    @property
    def url(self) -> str:
        return f"https://lichess.org/analysis/fromPosition/{self.fen_before_move.replace(' ', '_')}"
