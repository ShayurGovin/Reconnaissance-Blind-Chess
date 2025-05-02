import chess
from reconchess.utilities import without_opponent_pieces, is_illegal_castle

def main():
    inp = input()
    board = chess.Board(inp)

    moves = ['0000']

    for move in board.pseudo_legal_moves:
        moves.append(move.uci())
    
    for move in without_opponent_pieces(board).generate_castling_moves():
        if not is_illegal_castle(board, move) and move not in board.pseudo_legal_moves:
            moves.append(move.uci())

    for move in sorted(moves):
        print(move)


main()