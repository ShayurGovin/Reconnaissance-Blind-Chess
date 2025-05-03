import chess
import chess.engine
def main():
    boards = []
    moves = []
    inp = int(input())
    for i in range(inp):
        inp_board = input()
        board = chess.Board(inp_board)
        boards.append(board)
    for board in boards:
        colour = board.turn
        enemy_king_square = board.king(not colour)
        
        if enemy_king_square:
            enemy_king_attackers = board.attackers(colour, enemy_king_square)
            if enemy_king_attackers:
                attacker_square = enemy_king_attackers.pop()
                move = chess.Move(attacker_square, enemy_king_square)
                moves.append(move.uci())
                

        engine = None
        try:
            engine = chess.engine.SimpleEngine.popen_uci(r"C:\Users\Rohan\OneDrive\Documents\AI\Project\Reconnaissance-Blind-Chess\stockfish\stockfish.exe")
            board.turn = colour
            result = engine.play(board, chess.engine.Limit(time=0.5))
            move = result.move
            moves.append(move.uci())
        except chess.engine.EngineTerminatedError:
            print('Stockfish Engine died')
            move = chess.Move.null()
        except chess.engine.EngineError:
            print('Stockfish Engine bad state at "{}"'.format(board.fen()))
        finally:
            engine.quit()

    moves = sorted(moves)
    counter_Moves = []
    for move in moves:
        count = 0
        for compareMove in moves:
            if move == compareMove:
                count = count +1
        counter_Moves.append(count)
    
    common = max(counter_Moves)
    if common == 1:
        print(moves[0])
    else: 
        index = counter_Moves.index(common)
        print(moves[index])






main()