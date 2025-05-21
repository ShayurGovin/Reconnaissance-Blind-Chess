import chess.engine
import random
from reconchess import *
import os
from reconchess.utilities import without_opponent_pieces, is_illegal_castle
from collections import Counter
import chess

STOCKFISH_ENV_VAR = 'STOCKFISH_EXECUTABLE'


class RandomSensing(Player):

    def __init__(self):
        super().__init__()
        self.board = None
        self.color = None
        self.my_piece_captured_square = None
        self.current_board = None
        self.possible_states = None
        
        self.engine = chess.engine.SimpleEngine.popen_uci('/opt/stockfish/stockfish', setpgrp=True)
   
    def handle_game_start(self, color, board, opponent_name):
        self.board = board
        self.color = color
        self.current_board = board.copy(stack=False)
        self.possible_states = [self.current_board.copy(stack=False)]


    def handle_opponent_move_result(self, captured_my_piece, capture_square):
        self.my_piece_captured_square = capture_square
        if captured_my_piece:
            self.board.remove_piece_at(capture_square)
        new_states = []
        for state in self.possible_states:
            if state.turn != self.color:
                moves = []
                for move in state.pseudo_legal_moves:
                    moves.append(move)
                
                for move in without_opponent_pieces(state).generate_castling_moves():
                    if not is_illegal_castle(state, move) and move not in state.pseudo_legal_moves:
                        moves.append(move)

                for move in moves:
                    if captured_my_piece:
                        if move.to_square == capture_square and state.is_capture(move):
                            new_state = state.copy(stack=False)
                            new_state.push(move)
                            new_states.append(new_state)
                    else:
                        if not state.is_capture(move):
                            new_state = state.copy(stack=False)
                            new_state.push(move)
                            new_states.append(new_state)

        if new_states:
            self.possible_states = new_states

          
    def choose_sense(self, sense_actions, move_actions, seconds_left):
        valid_sense = []

        for sense in sense_actions:
            if 1 <= chess.square_file(sense) <= 6 and 1 <= chess.square_rank(sense) <= 6:
                valid_sense.append(sense) 

        return random.choice(valid_sense)


    def handle_sense_result(self, sense_result):
        valid_states = []
        for state in self.possible_states:
            count = 0
            for position, piece in sense_result:
                if state.piece_at(position) is not None and piece is not None:
                    if state.piece_at(position).symbol() == piece.symbol():
                        count = count + 1
                else:
                    if piece == None and state.piece_at(position) == None:
                        count = count +1

            if count == 9:
                    valid_states.append(state)


        if valid_states:    
            self.possible_states = valid_states


    def choose_move(self, move_actions: List[chess.Move], seconds_left: float) -> Optional[chess.Move]:
        N = len(self.possible_states)
        if N > 10000:
            self.possible_states = random.sample(self.possible_states, 10000)
            N = 10000
        if N <= 0:
            return random.choice(move_actions)

        moves = []
        time_per_state = 10.0 / N
        for state in self.possible_states:
            try:
                enemy_king_square = state.king(not self.color)
                if enemy_king_square:
                    enemy_king_attackers = state.attackers(self.color, enemy_king_square)
                    if enemy_king_attackers:
                        attacker_square = enemy_king_attackers.pop()
                        moves.append(chess.Move(attacker_square, enemy_king_square).uci())
                        continue

                state.turn = self.color
                state.clear_stack()
                result = self.engine.play(state, chess.engine.Limit(time=time_per_state))
                if result.move is not None:
                    moves.append(result.move.uci())
            except (chess.engine.EngineTerminatedError, chess.engine.EngineError):
                continue

        if not moves:
            return random.choice(move_actions)

        best_uci = min(Counter(moves).most_common(),key=lambda x: (-x[1], x[0]))[0]
        best_move = chess.Move.from_uci(best_uci)
        if best_move in move_actions:
            return best_move
        return random.choice(move_actions)


    def handle_move_result(self,requested_move: chess.Move,taken_move: chess.Move,captured_opponent_piece: bool,capture_square: int | None):
        new_states = []

        for state in self.possible_states:
            if requested_move in state.legal_moves and taken_move != requested_move:
                continue
            if taken_move not in state.pseudo_legal_moves:
                continue
            
            check_capture = state.is_capture(taken_move)

            if captured_opponent_piece:
                if not check_capture or taken_move.to_square != capture_square:
                    continue
            else:
                if check_capture:
                    continue
            new_state = state.copy(stack=False)
            new_state.push(taken_move)
            new_states.append(new_state)
        self.possible_states = new_states


    def handle_game_end(self, winner_color, win_reason,game_history):
        try:
            self.engine.quit()
        except chess.engine.EngineTerminatedError:
            pass