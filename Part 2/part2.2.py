import chess
from reconchess.utilities import without_opponent_pieces, is_illegal_castle

def main():
    inp = input()
    board = chess.Board(inp)

    moves = ['0000']

    states = []

    for move in board.pseudo_legal_moves:
        moves.append(move.uci())
    
    for move in without_opponent_pieces(board).generate_castling_moves():
        if not is_illegal_castle(board, move) and move not in board.pseudo_legal_moves:
            moves.append(move.uci())

    for move in sorted(moves):
        new_move = chess.Move.from_uci(move)
        board.push(new_move)
        states.append(board.fen())
        board.pop()
    
    for state in sorted(states):
        print(state)


main()