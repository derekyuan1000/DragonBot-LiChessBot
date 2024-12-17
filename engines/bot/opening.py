import pandas as pd
import chess
import chess.pgn
import random
import os


def play_opening(board):
    next_opening_moves = [];

    # If we go first, we just play e4
    if board.turn == chess.WHITE and board.fullmove_number == 1:
        next_opening_moves.append("e2e4")

    new_board = chess.Board()

    # Get the current directory of game.py
    current_directory = os.path.dirname(os.path.abspath(__file__))

    # Define the file path relative to the current directory
    file_path = os.path.join(current_directory, 'openings.csv')

    # Get all of the SAN notations
    chess_openings = pd.read_csv(file_path)

    chess_openings = chess_openings["moves"].tolist()

    # Loop over each opening
    # If it "contains" the same board position as our current board
    # Return it's next move
    for opening in chess_openings:
        moves_in_openings = opening.split();

        for index, move in enumerate(moves_in_openings):
            try:
                new_board.push_san(move)

                if board == new_board:
                    next_move = board.parse_san(moves_in_openings[index + 1]).uci()
                    next_opening_moves.append(next_move)
            except:
                break;

        new_board.reset()

    # If there are no more opening moves, return None
    if not next_opening_moves:
        return None

    # If there is valid openings, randomly choose the next move of them
    random_opening_from_array = random.choice(next_opening_moves)

    return random_opening_from_array