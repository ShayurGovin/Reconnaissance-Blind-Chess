import chess
import chess.engine
def main():
    inp = input()
    board = chess.Board(inp)
    colour = board.turn
    enemy_king_square = board.king(not colour)
    
    if enemy_king_square:
        enemy_king_attackers = board.attackers(colour, enemy_king_square)
        if enemy_king_attackers:
            attacker_square = enemy_king_attackers.pop()
            move = chess.Move(attacker_square, enemy_king_square)
            print(move.uci())
            return


    engine = None
    try:
        # engine = chess.engine.SimpleEngine.popen_uci(r"C:\Users\Rohan\OneDrive\Documents\AI\Project\Reconnaissance-Blind-Chess\stockfish\stockfish.exe")
        # engine = chess.engine.SimpleEngine.popen_uci(r"C:\Users\govin\OneDrive\Desktop\WITS\Year 4 Semester 1\Subjects\1 - Artificial Intelligence\Reconnaissance Blind Chess\Reconnaissance-Blind-Chess\stockfish\stockfish.exe")
        engine = chess.engine.SimpleEngine.popen_uci('/opt/stockfish/stockfish', setpgrp=True)

        board.turn = colour
        result = engine.play(board, chess.engine.Limit(time=0.5))
        move = result.move
    except chess.engine.EngineTerminatedError:
        print('Stockfish Engine died')
        move = chess.Move.null()
    except chess.engine.EngineError:
        print('Stockfish Engine bad state at "{}"'.format(board.fen()))
    finally:
        engine.quit()

    print(move.uci())

main()