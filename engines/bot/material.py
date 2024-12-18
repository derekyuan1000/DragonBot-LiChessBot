import chess

# Global dictionary to track rook positions and their open file status
rook_positions = {}

def get_material(board):
    # Weights
    pawn_weight = 100
    knight_weight = 310
    bishop_weight = 330
    rook_weight = 500
    queen_weight = 900
    king_weight = 20000

    white_pawn_count = len(board.pieces(chess.PAWN, chess.WHITE))
    white_rook_count = len(board.pieces(chess.ROOK, chess.WHITE))
    white_knight_count = len(board.pieces(chess.KNIGHT, chess.WHITE))
    white_bishop_count = len(board.pieces(chess.BISHOP, chess.WHITE))
    white_queen_count = len(board.pieces(chess.QUEEN, chess.WHITE))
    white_king_count = len(board.pieces(chess.KING, chess.WHITE))

    black_pawn_count = len(board.pieces(chess.PAWN, chess.BLACK))
    black_rook_count = len(board.pieces(chess.ROOK, chess.BLACK))
    black_knight_count = len(board.pieces(chess.KNIGHT, chess.BLACK))
    black_bishop_count = len(board.pieces(chess.BISHOP, chess.BLACK))
    black_queen_count = len(board.pieces(chess.QUEEN, chess.BLACK))
    black_king_count = len(board.pieces(chess.KING, chess.BLACK))

    rook_bonus = calculate_rook_bonus(board)

    # White
    white_pawn_weight = white_pawn_count * pawn_weight
    white_rook_weight = white_rook_count * rook_weight
    white_knight_weight = white_knight_count * knight_weight
    white_bishop_weight = white_bishop_count * bishop_weight
    white_queen_weight = white_queen_count * queen_weight
    white_king_weight = white_king_count * king_weight

    # Black
    black_pawn_weight = black_pawn_count * pawn_weight
    black_rook_weight = black_rook_count * rook_weight
    black_knight_weight = black_knight_count * knight_weight
    black_bishop_weight = black_bishop_count * bishop_weight
    black_queen_weight = black_queen_count * queen_weight
    black_king_weight = black_king_count * king_weight

    white_material = white_pawn_weight + white_rook_weight + white_knight_weight + white_bishop_weight + white_queen_weight + white_king_weight
    black_material = black_pawn_weight + black_rook_weight + black_knight_weight + black_bishop_weight + black_queen_weight + black_king_weight

    total_material = white_material - black_material + rook_bonus

    return total_material

def calculate_rook_bonus(board):
    def is_open_file(square):
        file_mask = chess.BB_FILES[chess.square_file(square)]
        white_pawns = board.pieces(chess.PAWN, chess.WHITE) & file_mask
        black_pawns = board.pieces(chess.PAWN, chess.BLACK) & file_mask
        return not (white_pawns or black_pawns)

    rook_bonus = 0
    
    for square in board.pieces(chess.ROOK, chess.WHITE):
        if is_open_file(square) and (square not in rook_positions or not rook_positions[square]):
            rook_bonus += 35
            rook_positions[square] = True
        else:
            rook_positions[square] = False

    for square in board.pieces(chess.ROOK, chess.BLACK):
        if is_open_file(square) and (square not in rook_positions or not rook_positions[square]):
            rook_bonus -= 35
            rook_positions[square] = True
        else:
            rook_positions[square] = False

    return rook_bonus
