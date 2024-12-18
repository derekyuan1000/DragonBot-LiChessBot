import chess
import numpy as np

from .opening import play_opening  # Adjusted comments to reflect imported behaviors

from .minimax import minimax  # Update to import modified minimax if external file was changed


from typing import Tuple, List  # New import to support type annotations

def get_move(board, depth):
    """
    Calculates the best move and the principal variation for both sides.
    """
    opening_move = play_opening(board)

    if opening_move:
        print("PLAYING OPENING MOVE: ", opening_move)
        return opening_move

    top_move = None;

    # Opposite of our minimax
    if board.turn == chess.WHITE:
      top_eval = -np.inf
    else:
      top_eval = np.inf

    for move in board.legal_moves:
        board.push(move)

        # WHEN WE ARE BLACK, WE WANT TRUE AND TO GRAB THE SMALLEST VALUE
        eval, pv = minimax(board, depth - 1, -np.inf, np.inf, board.turn)

        board.pop()

        if board.turn == chess.WHITE:
            if eval > top_eval:
                top_move = move
                top_eval = eval
        else:
            if eval < top_eval:
                top_move = move
                top_eval = eval

    print("CHOSEN MOVE (FOR CURRENT SIDE): ", top_move, "WITH EVAL: ", top_eval)
    print("PRINCIPAL VARIATION (FOR CURRENT SIDE): ", [top_move] + pv)

    # Simulate the opponent's perspective
    board.push(top_move)
    opponent_best_move = None
    opponent_top_eval = -np.inf if board.turn == chess.WHITE else np.inf

    for move in board.legal_moves:
        board.push(move)
        eval, pv = minimax(board, depth - 1, -np.inf, np.inf, board.turn)
        board.pop()

        if board.turn == chess.WHITE:
            if eval > opponent_top_eval:
                opponent_best_move = move
                opponent_top_eval = eval
        else:
            if eval < opponent_top_eval:
                opponent_best_move = move
                opponent_top_eval = eval

    board.pop()

    print("OPPONENT'S PERSPECTIVE (BEST MOVE): ", opponent_best_move, "WITH EVAL: ", opponent_top_eval)
    print("PRINCIPAL VARIATION (FOR OPPONENT SIDE): ", [opponent_best_move] + pv)
    return top_move