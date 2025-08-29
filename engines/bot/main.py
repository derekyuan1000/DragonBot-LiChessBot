import chess
import numpy as np
import time

from .opening import play_opening
from .minimax import minimax, order_moves


def get_move(board, depth=4, time_limit=None):
    """
    Get the best move using iterative deepening search (logs uniformly for diagnostics)
    """
    # First check if we have any legal moves
    legal_moves = list(board.legal_moves)
    if not legal_moves:
        return None

    opening_move = play_opening(board)

    if opening_move and opening_move in legal_moves:
        print(f"ENGINE ({'White' if board.turn == chess.WHITE else 'Black'}) opening move: {opening_move.uci()}")
        return opening_move

    # Use iterative deepening for better time management and move ordering
    best_move = None
    start_time = time.time()

    # Start with depth 1 and increase until we run out of time or reach max depth
    for current_depth in range(1, depth + 1):
        if time_limit and (time.time() - start_time) > time_limit * 0.8:
            break

        try:
            move, eval_score = search_best_move(board, current_depth)
            if move and move in legal_moves:
                best_move = move
                print(f"ENGINE ({'White' if board.turn == chess.WHITE else 'Black'}) depth {current_depth}: {best_move.uci()} eval {eval_score}")
        except Exception as e:
            print(f"Error in search at depth {current_depth}: {e}")
            break

    if not best_move or best_move not in legal_moves:
        # Fallback: just pick the first legal move
        best_move = legal_moves[0]

    print(f"ENGINE ({'White' if board.turn == chess.WHITE else 'Black'}) chosen move: {best_move.uci()}")
    return best_move


def search_best_move(board, depth):
    """Search for the best move at a given depth"""
    best_move = None
    best_eval = -np.inf

    moves = list(board.legal_moves)
    if not moves:
        return None, 0

    try:
        moves = order_moves(board, moves)  # Order moves for better pruning
    except Exception as e:
        print(f"Error in move ordering: {e}")
        # Use unordered moves as fallback

    # Store the current player before we start making moves
    current_player = board.turn

    for move in moves:
        if move not in board.legal_moves:
            continue

        try:
            board.push(move)
            # After pushing, board.turn has flipped, so we want the opposite of current_player
            eval_score = -minimax(board, depth - 1, -np.inf, np.inf, not current_player)
            board.pop()

            if eval_score > best_eval:
                best_eval = eval_score
                best_move = move
        except Exception as e:
            print(f"Error evaluating move {move}: {e}")
            try:
                board.pop()  # Make sure we pop if there was an error
            except:
                pass
            continue

    return best_move, best_eval
