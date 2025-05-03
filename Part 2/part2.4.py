import chess


def main():
    boards = []
    inp = int(input())
    for i in range(inp):
        inp_board = input()
        board = chess.Board(inp_board)
        boards.append(board)
    window = input()
    positions = window.split(";")
    valid_states = []
    for board in boards:
        count = 0
        for pos in positions:
            single_pos = pos.split(":")
            convert = chess.parse_square(single_pos[0])
            if board.piece_at(convert):
                if board.piece_at(convert).symbol() == single_pos[1]:
                    count = count + 1
            else:
                if single_pos[1] == '?':
                    count = count +1

        if count == 9:
            valid_states.append(board.fen())
    
    for state in sorted(valid_states):
        print(state)




main()