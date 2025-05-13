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

        self.engine = chess.engine.SimpleEngine.popen_uci(r"C:\Users\govin\OneDrive\Desktop\WITS\Year 4 Semester 1\Subjects\1 - Artificial Intelligence\Reconnaissance Blind Chess\Reconnaissance-Blind-Chess\stockfish\stockfish.exe")
        # self.engine = chess.engine.SimpleEngine.popen_uci(r"C:\Users\Rohan\OneDrive\Documents\AI\Project\Reconnaissance-Blind-Chess\stockfish\stockfish")
   
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
        N = len(self.possible_states)
        # 1) If no beliefs, pick randomly
        if N == 0:
            return random.choice(sense_actions)

        # 2) If you just lost a piece, sense where it was captured
        if self.my_piece_captured_square is not None:
            return self.my_piece_captured_square

        # 3) Sample if huge
        if N > 1000:
            sample = random.sample(self.possible_states, 1000)
        else:
            sample = self.possible_states
                
        N = len(sample)

        # 4) Compute weighted entropy per square
        VALUE = {'?':0.1,'P':1,'p':1,'N':3,'n':3,'B':3,'b':3,
                'R':5,'r':5,'Q':9,'q':9,'K':100,'k':100}

        entropy= {}
        for square in range(64):  # for each square on the board
            counts = Counter()
            
            # Count how many times each piece symbol appears at this square across all sampled boards
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
        
            max_piece_value = max(VALUE[sym] for sym in counts)
            entropy[square] = H * max_piece_value

        # 5) Compute opponent‐threat frequency per square
        threat = Counter()
        for state in sample:
            if state.turn != self.color:
                for move in state.pseudo_legal_moves:
                    threat[move.to_square] += 1

        # 6) Score each interior center by α·entropy + (1-α)·threat
        alpha = 0.7
        best = None
        best_score = -1.0

        for pos in sense_actions:
            f, r = chess.square_file(pos), chess.square_rank(pos)
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
        # add the pieces in the sense result to our board
        # for square, piece in sense_result:
        #     self.board.set_piece_at(square, piece)
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

        # new_Pos_states = []
        # if requested_move != taken_move:
        #     for state in self.possible_states:
        #         if not state.is_legal(requested_move):
        #             new_Pos_states.append(state)
        # else:
        #     for state in self.possible_states:
        #         if state.is_legal(requested_move):
        #             new_Pos_states.append(state)
        # self.possible_states = new_Pos_states

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
        # new_states = []

        # for state in self.possible_states:
        #     # 1) It must have been our turn in this hypothesis
        #     if state.turn != self.color:
        #         continue

        #     # 2) The actual move must be pseudo‐legal there
        #     if taken_move not in state.pseudo_legal_moves:
        #         continue

        #     # 3) The capture‐info must line up
        #     did_cap = state.is_capture(taken_move)
        #     if captured_opponent_piece:
        #         if not did_cap or taken_move.to_square != capture_square:
        #             continue
        #     else:
        #         if did_cap:
        #             continue

        #     # 4) It survives: push the actual move
        #     next_state = state.copy(stack=False)
        #     next_state.push(taken_move)
        #     new_states.append(next_state)

        #     # 5) Adopt the filtered list if any remain
        #     if new_states:
        #         # (optional: dedupe by FEN)
        #         unique = {s.fen(): s for s in new_states}
        #         self.possible_states = list(unique.values())

    def handle_game_end(self, winner_color, win_reason,game_history):
        try:
            self.engine.quit()
        except chess.engine.EngineTerminatedError:
            pass