import chess
from reconchess.utilities import without_opponent_pieces, is_illegal_castle

def main():
    inp = input()
    board = chess.Board(inp)

    moves = ['0000']

    pos = []

    for move in board.pseudo_legal_moves:
        moves.append(move.uci())
    
    for move in without_opponent_pieces(board).generate_castling_moves():
        if not is_illegal_castle(board, move) and move not in board.pseudo_legal_moves:
            moves.append(move.uci())

    for move in sorted(moves):
        new_board = board.copy()
        if move == '0000':
            new_board.push(chess.Move.null())
        else:
            new_board.push(chess.Move.from_uci(move))
        pos.append(new_board.fen())
    
    for p in sorted(pos):
        print(p)


        # new_move = chess.Move.from_uci(move)
        # board.push(new_move)
        # print(board.fen())


main()