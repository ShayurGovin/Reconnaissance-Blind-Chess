import chess.engine
import random
from reconchess import *
import os
from reconchess.utilities import without_opponent_pieces, is_illegal_castle
from collections import Counter
import chess
import math

STOCKFISH_ENV_VAR = 'STOCKFISH_EXECUTABLE'

class ImprovedAgent(Player):

    def __init__(self):
        super().__init__()
        self.board = None
        self.color = None
        self.my_piece_captured_square = None
        self.current_board = None
        self.possible_states = None

        self.opening_index = 0

        self.white_moves = [
            chess.Move.from_uci("b1c3"),
            chess.Move.from_uci("c3b5"),
            chess.Move.from_uci("b5d6"),
            chess.Move.from_uci("d6e8"),
        ]
        self.black_moves = [
            chess.Move.from_uci("b8c6"),
            chess.Move.from_uci("c6b4"),
            chess.Move.from_uci("b4d3"),
            chess.Move.from_uci("d3e1"),
        ]

        self.engine = chess.engine.SimpleEngine.popen_uci('/opt/stockfish/stockfish', setpgrp=True)

    def handle_game_start(self, color, board, opponent_name):
        self.board = board
        self.color = color
        self.current_board = board.copy(stack=False)
        self.possible_states = [self.current_board.copy(stack=False)]

        self.opening_index = 0


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
            self.possible_states = list({s.fen(): s for s in new_states}.values())


    def choose_sense(self, sense_actions, move_actions, seconds_left):
            N = len(self.possible_states)
            if N == 0:
                return random.choice(sense_actions)

            if self.my_piece_captured_square is not None:
                return self.my_piece_captured_square

            if N > 1000:
                sample = random.sample(self.possible_states, 1000)
            else:
                sample = self.possible_states
                    
            N = len(sample)

            WEIGHTS = {'?':0.1,'P':1,'p':1,'N':3,'n':3,'B':3,'b':3,
                    'R':5,'r':5,'Q':9,'q':9,'K':100,'k':100}

            entropy= {}
            for square in range(64):
                counts = Counter()
                
                for state in sample:
                    piece = state.piece_at(square)
                    if piece is None:
                        counts['?'] += 1
                    else:
                        counts[piece.symbol()] += 1

                H = 0.0
                for symbol in counts:
                    count = counts[symbol]
                    probability = count / N  
                    H -= probability * math.log2(probability)
            
                max_piece_value = max(WEIGHTS[sym] for sym in counts)
                entropy[square] = H * max_piece_value

            threat = Counter()
            for state in sample:
                if state.turn != self.color:
                    for move in state.pseudo_legal_moves:
                        threat[move.to_square] += 1

            alpha = 0.7
            best = None
            best_score = -1.0

            for pos in sense_actions:
                f  = chess.square_file(pos)
                r = chess.square_rank(pos)
                if not (1 <= f <= 6 and 1 <= r <= 6):
                    continue

                score = 0.0
                for df in (-1,0,1):
                    for dr in (-1,0,1):
                        square = chess.square(f+df, r+dr)
                        score += alpha * entropy.get(square,0) + (1-alpha) * threat.get(square,0)

                if score > best_score:
                    best_score, best = score, pos
            if best is not None:
                return best
            else:
                return random.choice(sense_actions)


    def handle_sense_result(self, sense_result):
        valid_states = []
        for state in self.possible_states:
            count = 0
            for position, piece in sense_result:
                sp = state.piece_at(position)
                if piece is not None and sp is not None:
                    if sp.symbol() == piece.symbol():
                        count += 1
                elif piece is None and sp is None:
                    count += 1
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

        if self.opening_index < 4:
            try:
                next_move = (self.white_moves if self.color == chess.WHITE else self.black_moves)[self.opening_index]
                if next_move in move_actions:
                    self.opening_index += 1
                    return next_move
            except IndexError:
                pass

        for state in self.possible_states:
            for move in state.legal_moves:
                if state.is_castling(move) and move in move_actions:
                    return move

        moves = []
        time_per_state = 10.0 / N
        for state in self.possible_states:
            try:
                enemy_king_square = state.king(not self.color)
                if enemy_king_square:
                    attackers = state.attackers(self.color, enemy_king_square)
                    if attackers:
                        attacker_square = attackers.pop()
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
        best_uci = min(Counter(moves).most_common(), key=lambda x: (-x[1], x[0]))[0]
        best_move = chess.Move.from_uci(best_uci)
        return best_move if best_move in move_actions else random.choice(move_actions)

    def handle_move_result(self, requested_move, taken_move, captured_opponent_piece, capture_square):
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

        self.possible_states = list({state.fen(): state for state in new_states}.values())

    def handle_game_end(self, winner_color, win_reason, game_history):
        try:
            self.engine.quit()
        except chess.engine.EngineTerminatedError:
            pass
