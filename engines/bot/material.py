import chess

def get_material(board):
    # Weights
    pw = 100
    kw = 310
    bw = 330
    rw = 500
    qw = 900
    kingw = 20000

    wp = len(board.pieces(chess.PAWN, chess.WHITE))
    wr = len(board.pieces(chess.ROOK, chess.WHITE))
    wk = len(board.pieces(chess.KNIGHT, chess.WHITE))
    wb = len(board.pieces(chess.BISHOP, chess.WHITE))
    wq = len(board.pieces(chess.QUEEN, chess.WHITE))
    wking = len(board.pieces(chess.KING, chess.WHITE))

    bp = len(board.pieces(chess.PAWN, chess.BLACK))
    br = len(board.pieces(chess.ROOK, chess.BLACK))
    bk = len(board.pieces(chess.KNIGHT, chess.BLACK))
    bb = len(board.pieces(chess.BISHOP, chess.BLACK))
    bq = len(board.pieces(chess.QUEEN, chess.BLACK))
    bking = len(board.pieces(chess.KING, chess.BLACK))

    # White
    wpw = wp * pw
    # Rook weight increases for less pawns
    wrw = wr * rw
    # Knight weight goes down for each enemy pawn gone (8 pawns)
    wkw = wk * kw
    wbw = wb * bw
    wqw = wq * qw
    wkingw = wking * kingw

    # Black
    bpw = bp * pw
    # Rook weight increases for less pawns
    brw = br * rw
    # Knight weight goes down for each enemy pawn gone  (8 pawns)
    bkw = bk * kw
    bbw = bb * bw
    bqw = bq * qw
    bkingw = bking * kingw

    white_material = wpw + wrw + wkw + wbw + wqw + wkingw
    black_material = bpw + brw + bkw + bbw + bqw + bkingw

    total_material = white_material - black_material

    return total_material