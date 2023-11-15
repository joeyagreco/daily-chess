import os

import chess
from stockfish import Stockfish

from enumeration.ChessColor import ChessColor
from model.ChessGameV2 import ChessGameV2
from model.MoveEval import MoveEval


def get_worst_move_for_user(
    *,
    chess_game: ChessGameV2,
    username: str,
    evaluation_depth: int,
    stockfish_executable_name: str,
    stop_after_eval_change_of: int,
) -> MoveEval:
    """
    Returns the worst move from the given game for the user with the given username.
    """

    def convert_eval(ev: int, evaluate_for_white: bool) -> int:
        # change to be a positive eval if good and negative eval if bad for both white and black
        return ev if evaluate_for_white else -ev

    stockfish_relative_path = f"../bin/{stockfish_executable_name}"
    stockfish_absolute_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), stockfish_relative_path)
    )
    print(f"ATTEMPTING TO LOAD STOCKFISH FROM: '{stockfish_absolute_path}'")
    stockfish = Stockfish(stockfish_absolute_path)
    print(f"SUCCESSFULLY LOADED STOCKFISH")

    MATE_VALUE = -10_000
    board = chess.Board()
    stockfish.set_depth(evaluation_depth)

    move_evals: list[MoveEval] = []

    worst_change = 0
    best_move = None
    last_eval = 0

    moves = chess_game.moves.split(" ")
    evaluate_for_white = chess_game.color_for_user(username) == ChessColor.WHITE

    white_turn = True
    for move in moves:
        if worst_change <= stop_after_eval_change_of:
            break
        pre_move_fen = board.fen()
        board.push_san(move)
        fen = board.fen()
        stockfish.set_fen_position(fen, send_ucinewgame_token=True)
        # evaluate only for the color we want to evaluate for
        if evaluate_for_white == white_turn:
            raw_eval = stockfish.get_evaluation()
            # we can either get centipawn or mate
            if raw_eval["type"] == "mate":
                current_eval = MATE_VALUE + abs(raw_eval["value"])
            else:
                current_eval = convert_eval(raw_eval["value"], evaluate_for_white)

            current_change = current_eval - last_eval
            move_eval = MoveEval(
                actual_move=board.peek().uci(),
                eval_change=current_change,
                fen_before_move=pre_move_fen,
            )
            if current_change < worst_change:
                worst_change = current_change
                stockfish.set_fen_position(pre_move_fen, send_ucinewgame_token=True)
                best_move = stockfish.get_best_move()
                move_eval.engine_best_move = best_move
            last_eval = current_eval
            move_evals.append(move_eval)

        white_turn = not white_turn

    sorted_move_evals = sorted(move_evals, key=lambda x: x.eval_change, reverse=False)
    return sorted_move_evals[0]
