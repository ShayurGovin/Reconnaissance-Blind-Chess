import chess.engine
import random
from reconchess import *
import os
from reconchess.utilities import without_opponent_pieces, is_illegal_castle
from collections import Counter
import chess

STOCKFISH_ENV_VAR = 'STOCKFISH_EXECUTABLE'


class MyAgent(Player):

    def __init__(self):
        super().__init__()
        self.board = None
        self.color = None
        self.my_piece_captured_square = None
        self.current_board = None
        self.possible_states = None

        #self.engine = chess.engine.SimpleEngine.popen_uci(r"C:\Users\govin\OneDrive\Desktop\WITS\Year 4 Semester 1\Subjects\1 - Artificial Intelligence\Reconnaissance Blind Chess\Reconnaissance-Blind-Chess\stockfish\stockfish.exe")
        self.engine = chess.engine.SimpleEngine.popen_uci(r"C:\Users\Rohan\OneDrive\Documents\AI\Project\Reconnaissance-Blind-Chess\stockfish\stockfish.exe")
   
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
                            state.push(move)
                            new_states.append(state.copy(stack=False))
                            state.pop()
                    else:
                        if not state.is_capture(move):
                            state.push(move)
                            new_states.append(state.copy(stack=False))
                            state.pop()

        if new_states:
            self.possible_states = new_states
                        



    def choose_sense(self, sense_actions, move_actions, seconds_left):
        valid_sense = []

        for sense in sense_actions:
            if 1 <= chess.square_file(sense) <= 6 and 1 <= chess.square_rank(sense) <= 6:
                valid_sense.append(sense) 

        return random.choice(valid_sense)

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
        # 1) Prune your belief list
        N = len(self.possible_states)
        if N > 10000:
            self.possible_states = random.sample(self.possible_states, 10000)
            N = 10000

        moves = []

        # 2) King‐capture override
        for state in self.possible_states:
            enemy_king_square = state.king(not self.color)
            if enemy_king_square:
                enemy_king_attackers = state.attackers(self.color, enemy_king_square)
                if enemy_king_attackers:
                    attacker_square = enemy_king_attackers.pop()
                    moves.append(chess.Move(attacker_square, enemy_king_square).uci())

        # 3) Stockfish votes with a fresh engine
        engine_path = r"C:\Users\Rohan\OneDrive\Documents\AI\Project\Reconnaissance-Blind-Chess\stockfish\stockfish.exe"
        time_per_state = 10.0 / max(N, 1)
        with chess.engine.SimpleEngine.popen_uci(engine_path) as engine:
            for state in self.possible_states:
                try:
                    state.turn = self.color
                    state.clear_stack()
                    result = engine.play(state, chess.engine.Limit(time=time_per_state))
                    moves.append(result.move.uci())
                except (chess.engine.EngineTerminatedError, chess.engine.EngineError):
                    # skip this state if Stockfish fails
                    continue

        # 4) If we got no moves at all, just pick a random legal one
        if not moves:
            return random.choice(move_actions)

        # 5) Tally and pick the top‐voted move
        best_uci = min(
            Counter(moves).most_common(),
            key=lambda x: (-x[1], x[0])
        )[0]
        best_move = chess.Move.from_uci(best_uci)
        if best_move in move_actions:
            return best_move

        # 6) Fallback
        return random.choice(move_actions)


    def handle_move_result(self,requested_move: chess.Move,taken_move: chess.Move,captured_opponent_piece: bool,capture_square: int | None):
        """
        Keeps only those candidate states where:
        - it was our turn
        - `taken_move` is legal in that state
        - the capture‐or‐no‐capture matches `captured_opponent_piece`
        - if a capture happened, it landed on `capture_square`
        Then advances each surviving state by pushing `taken_move`.
        """
        new_states = []

        for state in self.possible_states:
            # only consider boards where it was actually our turn
            if state.turn != self.color:
                continue

            # the move actually played must be legal here
            if taken_move not in state.legal_moves:
                continue

            # enforce the capture feedback
            did_cap = state.is_capture(taken_move)
            if captured_opponent_piece:
                # must have been a capture, on the reported square
                if not did_cap or taken_move.to_square != capture_square:
                    continue
            else:
                # must *not* have been a capture
                if did_cap:
                    continue

            # this state survives: advance it
            nxt = state.copy(stack=False)
            nxt.push(taken_move)
            new_states.append(nxt)

        # if at least one survives, adopt the filtered list
        if new_states:
            # optional: dedupe by FEN
            unique = {s.fen(): s for s in new_states}
            self.possible_states = list(unique.values())


    def handle_game_end(self, winner_color, win_reason,game_history):
        try:
            self.engine.quit()
        except chess.engine.EngineTerminatedError:
            pass