import chess
import chess.engine
from collections import Counter

def main():
    boards = []
    moves = []

    inp = int(input())
    for i in range(inp):
        inp_board = input()
        board = chess.Board(inp_board)
        boards.append(board)
    
    try:
        # engine = chess.engine.SimpleEngine.popen_uci(r"C:\Users\govin\OneDrive\Desktop\WITS\Year 4 Semester 1\Subjects\1 - Artificial Intelligence\Reconnaissance Blind Chess\Reconnaissance-Blind-Chess\stockfish\stockfish.exe")
        engine = chess.engine.SimpleEngine.popen_uci('/opt/stockfish/stockfish', setpgrp=True)


        for board in boards:
            colour = board.turn
            enemy_king_square = board.king(not colour)
            
            if enemy_king_square:
                enemy_king_attackers = board.attackers(colour, enemy_king_square)
                if enemy_king_attackers:
                    attacker_square = enemy_king_attackers.pop()
                    move = chess.Move(attacker_square, enemy_king_square)
                    moves.append(move.uci())
                    continue
            
            board.turn = colour
            result = engine.play(board, chess.engine.Limit(time=0.1))
            move = result.move
            moves.append(move.uci())
    
    except chess.engine.EngineTerminatedError:
        print('Stockfish Engine died')
        move = chess.Move.null()
    except chess.engine.EngineError:
        print('Stockfish Engine bad state at "{}"'.format(board.fen()))
    finally:
        engine.quit()


    move = min(Counter(moves).most_common(), key=lambda x: (-x[1], x[0]))[0]
    print(move)

main()