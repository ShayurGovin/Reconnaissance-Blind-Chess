import chess

def moveexecution(fen, moveuci):
    board = chess.Board(fen)
    move = chess.Move.from_uci(moveuci)
    board.push(move)
    print(board.fen())

def main():
    fen = input()
    moveuci = input()
    moveexecution(fen, moveuci)

main()