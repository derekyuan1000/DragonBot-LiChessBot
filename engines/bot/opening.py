import pandas as pd
import chess
import chess.pgn
import random
import os


def play_opening(board):
    next_opening_moves = []

    # If we go first, we just play e4
    if board.turn == chess.WHITE and board.fullmove_number == 1:
        try:
            move = chess.Move.from_uci("e2e4")
            if move in board.legal_moves:
                next_opening_moves.append(move)
        except:
            pass

    new_board = chess.Board()

    # Get the current directory of opening.py
    current_directory = os.path.dirname(os.path.abspath(__file__))

    # Define the file path relative to the current directory
    file_path = os.path.join(current_directory, 'openings.csv')

    # Check if openings file exists
    if not os.path.exists(file_path):
        return random.choice(next_opening_moves) if next_opening_moves else None

    try:
        # Get all of the SAN notations
        chess_openings = pd.read_csv(file_path)
        chess_openings = chess_openings["moves"].tolist()

        # Loop over each opening
        # If it "contains" the same board position as our current board
        # Return it's next move
        for opening in chess_openings:
            try:
                moves_in_openings = opening.split()

                for index, move in enumerate(moves_in_openings):
                    try:
                        new_board.push_san(move)

                        if board == new_board:
                            if index + 1 < len(moves_in_openings):
                                next_move_san = moves_in_openings[index + 1]
                                next_move = board.parse_san(next_move_san)
                                if next_move in board.legal_moves:
                                    next_opening_moves.append(next_move)
                    except:
                        break

                new_board.reset()
            except:
                continue

    except Exception as e:
        print(f"Error loading opening book: {e}")

    # If there are no more opening moves, return None
    if not next_opening_moves:
        return None

    # If there are valid openings, randomly choose one
    return random.choice(next_opening_moves)
