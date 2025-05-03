import chess
from reconchess.utilities import without_opponent_pieces, is_illegal_castle

def main():
    chess_alphabet = ['a','b','c','d','e','f','g','h']
    inp = input()
    board = chess.Board(inp)
    pos_inp = input()
    convert = chess_alphabet.index(pos_inp[0]) + 8 * (int(pos_inp[1])-1)
    moves = []

    states = []

    for move in board.pseudo_legal_moves:
        moves.append(move)
    
    for move in without_opponent_pieces(board).generate_castling_moves():
        if not is_illegal_castle(board, move) and move not in board.pseudo_legal_moves:
            moves.append(move)

    for move in moves:
        if move.to_square == convert:
            board.push(move)
            states.append(board.fen())
            board.pop()
    
    for state in sorted(states):
        print(state)
    
    



main()