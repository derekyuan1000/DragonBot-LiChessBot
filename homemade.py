"""
Some example classes for people who want to create a homemade bot.

With these classes, bot makers will not have to implement the UCI or XBoard interfaces themselves.
"""
from engines.bot.main import get_move
import chess
from chess.engine import PlayResult, Limit
import random
from lib.engine_wrapper import MinimalEngine
from lib.types import MOVE, HOMEMADE_ARGS_TYPE
import logging


# Use this logger variable to print messages to the console or log files.
# logger.info("message") will always print "message" to the console or log file.
# logger.debug("message") will only print "message" if verbose logging is enabled.
logger = logging.getLogger(__name__)


class ExampleEngine(MinimalEngine):
    """An example engine that all homemade engines inherit."""

    pass


class PyBot(ExampleEngine):
    def search(self, board: chess.Board, time_limit: Limit, ponder: bool, draw_offered: bool,
               root_moves: MOVE) -> PlayResult:
        """
        Use the custom bot engine from engines/bot/main.py to calculate moves.
        """
        print("GETTING MOVE!")

        # Get legal moves first and validate everything
        legal_moves_list = list(board.legal_moves)
        if not legal_moves_list:
            logger.error("No legal moves available!")
            return PlayResult(None, None)

        # Calculate available time based on time control
        if isinstance(time_limit.time, (int, float)) and time_limit.time is not None:
            my_time = time_limit.time
            my_inc = 0
        elif board.turn == chess.WHITE:
            my_time = time_limit.white_clock if isinstance(time_limit.white_clock, (int, float)) else 5
            my_inc = time_limit.white_inc if isinstance(time_limit.white_inc, (int, float)) else 0
        else:
            my_time = time_limit.black_clock if isinstance(time_limit.black_clock, (int, float)) else 5
            my_inc = time_limit.black_inc if isinstance(time_limit.black_inc, (int, float)) else 0

        # Convert to seconds if needed
        if my_time > 1000:  # Assume it's in milliseconds
            my_time_seconds = my_time / 1000
        else:  # Assume it's already in seconds
            my_time_seconds = max(0.1, my_time)  # Ensure minimum time

        # Determine game stage and depth
        move_count = len(board.move_stack)
        if move_count < 20:  # Opening
            stage = "opening"
            depth = 3
        elif move_count < 40:  # Middlegame
            stage = "middlegame"
            depth = 4
        else:  # Endgame
            stage = "endgame"
            depth = 4

        # Calculate thinking time
        if my_time_seconds > 60:
            think_time = min(10, my_time_seconds * 0.1)
        elif my_time_seconds > 10:
            think_time = min(5, my_time_seconds * 0.2)
        else:
            think_time = min(2, my_time_seconds * 0.3)

        print(f"Game stage: {stage}, Move {move_count + 1}, Time: {my_time_seconds:.1f}s, Depth: {depth}")

        # Get move from the bot engine with multiple validation layers
        move = None
        try:
            # Try to get move from engine
            engine_move = get_move(board, depth)

            # Validate the engine move thoroughly
            if engine_move is not None and engine_move in legal_moves_list:
                move = engine_move
                print(f"Engine chose: {move}")
            else:
                print(f"Engine returned invalid move: {engine_move}")
                move = None

        except Exception as e:
            logger.error(f"Error getting move from engine: {e}")
            move = None

        # Handle root_moves constraint if specified
        if isinstance(root_moves, list) and root_moves:
            # Filter root_moves to only include legal moves
            valid_root_moves = [m for m in root_moves if m in legal_moves_list]

            if valid_root_moves:
                if move is None or move not in valid_root_moves:
                    move = random.choice(valid_root_moves)
                    print(f"Selected from root_moves: {move}")
            else:
                logger.error("No valid moves in root_moves constraint!")
                move = random.choice(legal_moves_list)

        # Final fallback - ensure we always have a legal move
        if move is None or move not in legal_moves_list:
            move = random.choice(legal_moves_list)
            print(f"Fallback move selected: {move}")

        # Final validation before returning
        if move not in board.legal_moves:
            logger.error(f"CRITICAL: Selected move {move} is not legal! Using first legal move.")
            move = legal_moves_list[0]

        print(f"FINAL MOVE: {move}")
        return PlayResult(move, None)




class RandomMove(ExampleEngine):
    """Get a random move."""

    def search(self, board: chess.Board, *args: HOMEMADE_ARGS_TYPE) -> PlayResult:
        """Choose a random move."""
        return PlayResult(random.choice(list(board.legal_moves)), None)


class Alphabetical(ExampleEngine):
    """Get the first move when sorted by san representation."""

    def search(self, board: chess.Board, *args: HOMEMADE_ARGS_TYPE) -> PlayResult:
        """Choose the first move alphabetically."""
        moves = list(board.legal_moves)
        moves.sort(key=board.san)
        return PlayResult(moves[0], None)


class FirstMove(ExampleEngine):
    """Get the first move when sorted by uci representation."""

    def search(self, board: chess.Board, *args: HOMEMADE_ARGS_TYPE) -> PlayResult:
        """Choose the first move alphabetically in uci representation."""
        moves = list(board.legal_moves)
        moves.sort(key=str)
        return PlayResult(moves[0], None)


class ComboEngine(ExampleEngine):
    """
    Get a move using multiple different methods.

    This engine demonstrates how one can use `time_limit`, `draw_offered`, and `root_moves`.
    """

    def search(self, board: chess.Board, time_limit: Limit, ponder: bool, draw_offered: bool, root_moves: MOVE) -> PlayResult:
        """
        Choose a move using multiple different methods.

        :param board: The current position.
        :param time_limit: Conditions for how long the engine can search (e.g. we have 10 seconds and search up to depth 10).
        :param ponder: Whether the engine can ponder after playing a move.
        :param draw_offered: Whether the bot was offered a draw.
        :param root_moves: If it is a list, the engine should only play a move that is in `root_moves`.
        :return: The move to play.
        """
        if isinstance(time_limit.time, int):
            my_time = time_limit.time
            my_inc = 0
        elif board.turn == chess.WHITE:
            my_time = time_limit.white_clock if isinstance(time_limit.white_clock, int) else 0
            my_inc = time_limit.white_inc if isinstance(time_limit.white_inc, int) else 0
        else:
            my_time = time_limit.black_clock if isinstance(time_limit.black_clock, int) else 0
            my_inc = time_limit.black_inc if isinstance(time_limit.black_inc, int) else 0

        possible_moves = root_moves if isinstance(root_moves, list) else list(board.legal_moves)

        if my_time / 60 + my_inc > 10:
            # Choose a random move.
            move = random.choice(possible_moves)
        else:
            # Choose the first move alphabetically in uci representation.
            possible_moves.sort(key=str)
            move = possible_moves[0]
        return PlayResult(move, None, draw_offered=draw_offered)
