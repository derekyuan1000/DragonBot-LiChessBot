from .evaluation import get_evaluation
import numpy as np
import chess


def order_moves(board, moves):
    """Simple move ordering to improve alpha-beta pruning efficiency"""
    move_scores = []

    for move in moves:
        score = 0

        # Prioritize captures
        if board.is_capture(move):
            victim = board.piece_at(move.to_square)
            if victim:
                piece_values = {chess.PAWN: 1, chess.KNIGHT: 3, chess.BISHOP: 3,
                               chess.ROOK: 5, chess.QUEEN: 9, chess.KING: 100}
                score += piece_values.get(victim.piece_type, 0) * 10

        # Prioritize checks
        board.push(move)
        if board.is_check():
            score += 50
        board.pop()

        # Prioritize promotions
        if move.promotion:
            score += 80

        move_scores.append((move, score))

    # Sort by score descending
    move_scores.sort(key=lambda x: x[1], reverse=True)
    return [move for move, score in move_scores]


def minimax(board, depth, alpha, beta, maximizing_player):
    if depth == 0 or board.is_game_over():
        return get_evaluation(board)

    # Order moves for better pruning
    moves = list(board.legal_moves)
    moves = order_moves(board, moves)

    if maximizing_player:
        max_eval = -np.inf
        for move in moves:
            board.push(move)
            eval = minimax(board, depth - 1, alpha, beta, False)
            board.pop()
            max_eval = max(max_eval, eval)
            alpha = max(alpha, eval)
            if beta <= alpha:
                break
        return max_eval
    else:
        min_eval = np.inf
        for move in moves:
            board.push(move)
            eval = minimax(board, depth - 1, alpha, beta, True)
            board.pop()
            min_eval = min(min_eval, eval)
            beta = min(beta, eval)
            if beta <= alpha:
                break
        return min_eval