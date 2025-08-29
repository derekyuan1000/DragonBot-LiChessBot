from .material import get_material
import chess
from . import positions

def get_evaluation(board):
    # Check for game ending conditions
    if board.is_checkmate():
        return -9999 if board.turn else 9999
    if board.is_stalemate() or board.is_insufficient_material():
        return 0

    eval_score = 0

    # Apply evolved evaluation weights from champion bot
    material_weight = 0.9097338598808318  # Evolved from 1.0
    position_weight = 0.3
    king_safety_weight = 0.8
    pawn_structure_weight = 0.4
    piece_activity_weight = 0.6
    center_control_weight = 0.5

    # Material and piece-square tables with evolved weights
    eval_score += get_material(board) * material_weight
    eval_score += get_piece_square_tables(board) * position_weight

    # Additional positional factors with evolved weights
    eval_score += evaluate_king_safety(board) * king_safety_weight
    eval_score += evaluate_pawn_structure(board) * pawn_structure_weight
    eval_score += evaluate_piece_activity(board) * piece_activity_weight
    eval_score += evaluate_center_control(board) * center_control_weight

    return eval_score

def get_piece_square_tables(board):
    """Calculate piece-square table bonuses"""
    score = 0

    # Pawns
    for square in board.pieces(chess.PAWN, chess.WHITE):
        score += positions.pawn[square]
    for square in board.pieces(chess.PAWN, chess.BLACK):
        score -= positions.pawn[chess.square_mirror(square)]

    # Knights
    for square in board.pieces(chess.KNIGHT, chess.WHITE):
        score += positions.knight[square]
    for square in board.pieces(chess.KNIGHT, chess.BLACK):
        score -= positions.knight[chess.square_mirror(square)]

    # Bishops
    for square in board.pieces(chess.BISHOP, chess.WHITE):
        score += positions.bishop[square]
    for square in board.pieces(chess.BISHOP, chess.BLACK):
        score -= positions.bishop[chess.square_mirror(square)]

    # Rooks
    for square in board.pieces(chess.ROOK, chess.WHITE):
        score += positions.rook[square]
    for square in board.pieces(chess.ROOK, chess.BLACK):
        score -= positions.rook[chess.square_mirror(square)]

    # Queens
    for square in board.pieces(chess.QUEEN, chess.WHITE):
        score += positions.queen[square]
    for square in board.pieces(chess.QUEEN, chess.BLACK):
        score -= positions.queen[chess.square_mirror(square)]

    # Kings
    for square in board.pieces(chess.KING, chess.WHITE):
        score += positions.king[square]
    for square in board.pieces(chess.KING, chess.BLACK):
        score -= positions.king[chess.square_mirror(square)]

    return score

def evaluate_king_safety(board):
    """Evaluate king safety for both sides with evolved castling bonus"""
    score = 0

    # Evolved castling bonus from champion bot
    castling_bonus = 25.11233112577063  # Evolved from 20

    # White king safety
    white_king_square = board.king(chess.WHITE)
    if white_king_square:
        # Penalty for exposed king in middle game
        if count_material(board) > 2000:  # Middle game
            king_file = chess.square_file(white_king_square)
            if 2 <= king_file <= 5:  # King in center files
                score -= 50

        # Evolved bonus for castling rights
        if board.has_kingside_castling_rights(chess.WHITE) or board.has_queenside_castling_rights(chess.WHITE):
            score += castling_bonus

    # Black king safety
    black_king_square = board.king(chess.BLACK)
    if black_king_square:
        if count_material(board) > 2000:
            king_file = chess.square_file(black_king_square)
            if 2 <= king_file <= 5:
                score += 50

        if board.has_kingside_castling_rights(chess.BLACK) or board.has_queenside_castling_rights(chess.BLACK):
            score -= castling_bonus

    return score

def evaluate_pawn_structure(board):
    """Evaluate pawn structure with evolved penalties"""
    score = 0

    # Evolved penalty values from champion bot
    doubled_pawn_penalty = 20  # Unchanged
    isolated_pawn_penalty = 10.80904763023034  # Evolved from 15

    # Doubled pawns penalty
    for file in range(8):
        white_pawns_on_file = len([sq for sq in board.pieces(chess.PAWN, chess.WHITE) if chess.square_file(sq) == file])
        black_pawns_on_file = len([sq for sq in board.pieces(chess.PAWN, chess.BLACK) if chess.square_file(sq) == file])

        if white_pawns_on_file > 1:
            score -= doubled_pawn_penalty * (white_pawns_on_file - 1)
        if black_pawns_on_file > 1:
            score += doubled_pawn_penalty * (black_pawns_on_file - 1)

    # Isolated pawns penalty with evolved value
    for square in board.pieces(chess.PAWN, chess.WHITE):
        if is_isolated_pawn(board, square, chess.WHITE):
            score -= isolated_pawn_penalty
    for square in board.pieces(chess.PAWN, chess.BLACK):
        if is_isolated_pawn(board, square, chess.BLACK):
            score += isolated_pawn_penalty

    return score

def evaluate_piece_activity(board):
    """Evaluate piece mobility and activity"""
    score = 0

    # Count legal moves (mobility)
    original_turn = board.turn

    board.turn = chess.WHITE
    white_mobility = len(list(board.legal_moves))

    board.turn = chess.BLACK
    black_mobility = len(list(board.legal_moves))

    board.turn = original_turn

    score += (white_mobility - black_mobility) * 2

    return score

def evaluate_center_control(board):
    """Evaluate control of center squares"""
    score = 0
    center_squares = [chess.E4, chess.E5, chess.D4, chess.D5]

    for square in center_squares:
        # Check if square is attacked by white
        if board.is_attacked_by(chess.WHITE, square):
            score += 10
        # Check if square is attacked by black
        if board.is_attacked_by(chess.BLACK, square):
            score -= 10

    return score

def count_material(board):
    """Count total material on board"""
    material = 0
    piece_values = {chess.PAWN: 100, chess.KNIGHT: 310, chess.BISHOP: 330,
                   chess.ROOK: 513, chess.QUEEN: 900}  # Using evolved rook value

    for piece_type in piece_values:
        material += len(board.pieces(piece_type, chess.WHITE)) * piece_values[piece_type]
        material += len(board.pieces(piece_type, chess.BLACK)) * piece_values[piece_type]

    return material

def is_isolated_pawn(board, square, color):
    """Check if a pawn is isolated"""
    file = chess.square_file(square)
    adjacent_files = [f for f in [file - 1, file + 1] if 0 <= f <= 7]

    for adj_file in adjacent_files:
        for rank in range(8):
            adj_square = chess.square(adj_file, rank)
            piece = board.piece_at(adj_square)
            if piece and piece.piece_type == chess.PAWN and piece.color == color:
                return False
    return True
