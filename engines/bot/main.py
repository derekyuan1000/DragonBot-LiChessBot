import chess
import numpy as np

from .opening import play_opening
from .minimax import minimax
from chess import Board


def get_move(board, depth):
    def minimax(board, depth, alpha, beta, maximizing_player, line):
        # Added placeholder for adaption to store moves
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

        # Calculate and store the principal variation for the line
        line = []
        eval = minimax(board, depth - 1, -np.inf, np.inf, board.turn, line)
        board.pop()
        print("MOVE:", move, " LINE: ", line, " EVAL: ", eval)

        if board.turn == chess.WHITE:
            if eval > top_eval:
                top_move = move
                top_eval = eval
        else:
            if eval < top_eval:
                top_move = move
                top_eval = eval

    print("CHOSEN MOVE: ", top_move, "WITH EVAL: ", top_eval)
    return top_move