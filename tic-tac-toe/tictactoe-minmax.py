import math

# Board representation:
# Board is a list of 9 elements: ['X', 'O', ' ', ' ', ...]
# Indexes:
# 0 | 1 | 2
# 3 | 4 | 5
# 6 | 7 | 8


def print_board(board):
    print()
    for i in range(0, 9, 3):
        print(board[i], "|", board[i+1], "|", board[i+2])
    print()


def available_moves(board):
    return [i for i, spot in enumerate(board) if spot == " "]


def check_winner(board):
    win_states = [
        (0,1,2), (3,4,5), (6,7,8),     # rows
        (0,3,6), (1,4,7), (2,5,8),     # columns
        (0,4,8), (2,4,6)               # diagonals
    ]

    for (a, b, c) in win_states:
        if board[a] == board[b] == board[c] and board[a] != " ":
            return board[a]

    if " " not in board:
        return "draw"

    return None


def minimax(board, depth, is_maximizing):
    winner = check_winner(board)

    # Scoring
    if winner == "X":
        return 10 - depth
    elif winner == "O":
        return depth - 10
    elif winner == "draw":
        return 0

    if is_maximizing:
        best_score = -math.inf
        for move in available_moves(board):
            board[move] = "X"
            score = minimax(board, depth+1, False)
            board[move] = " "
            best_score = max(best_score, score)
        return best_score
    else:
        best_score = math.inf
        for move in available_moves(board):
            board[move] = "O"
            score = minimax(board, depth+1, True)
            board[move] = " "
            best_score = min(best_score, score)
        return best_score


def computer_move(board):
    best_score = -math.inf
    best_move = None

    for move in available_moves(board):
        board[move] = "X"  # computer plays X
        score = minimax(board, 0, False)
        board[move] = " "
        if score > best_score:
            best_score = score
            best_move = move

    board[best_move] = "X"


def play():
    board = [" "] * 9
    human = "O"
    computer = "X"

    print("You are O. Computer is X.")
    print_board(board)

    while True:
        # Human move
        move = int(input("Your move (0-8): "))
        if board[move] != " ":
            print("Spot taken. Try again.")
            continue

        board[move] = human
        print_board(board)

        if check_winner(board):
            break

        # Computer move
        computer_move(board)
        print("Computer move:")
        print_board(board)

        result = check_winner(board)
        if result:
            break

    result = check_winner(board)
    if result == "draw":
        print("It's a draw!")
    else:
        print(result, "wins!")


# Run the game
if __name__ == "__main__":
    play()
