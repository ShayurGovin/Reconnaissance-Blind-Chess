# Test against other bots
# rc-bot-match Part4\baseline_bot.py Part4\trout_bot.py


import chess
import random
from reconchess import *

class RandomSensing(Player):
    def __init__(self):
        self.color = None
        self.current_board = chess.Board()
        self.possible_states = [self.current_board.copy()]
        self.engine = chess.engine.SimpleEngine.popen_uci(r"C:\Users\govin\OneDrive\Desktop\WITS\Year 4 Semester 1\Subjects\1 - Artificial Intelligence\Reconnaissance Blind Chess\Reconnaissance-Blind-Chess\stockfish\stockfish.exe")

    def handle_game_start(self, color: Color, board: chess.Board, opponent_name: str):
        self.color = color
        self.current_board = board.copy()
        self.possible_states = [self.current_board.copy()]

    def handle_opponent_move_result(self, captured_my_piece, capture_square):
        pass

    def choose_sense(self, sense_actions, move_actions, seconds_left):
        return random.choice(sense_actions)

    def handle_sense_result(self, sense_result):
        pass

    def choose_move(self, move_actions, seconds_left):
        return random.choice(move_actions)

    def handle_move_result(self, requested_move, taken_move, captured_opponent_piece, capture_square):
        pass

    def handle_game_end(self, winner_color, win_reason, game_history):
        pass
