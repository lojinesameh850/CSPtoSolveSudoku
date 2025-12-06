import random
def generate_board(difficulty):
    clue_counts = {
        "easy" : 45,
        "intermediate" : 33,
        "hard" : 17
    }
    clues = clue_counts[difficulty]
    board = create_empty_board()
    i = 0
    while i < clues:
        r = random.randint(0,8)
        c = random.randint(0,8)
        if(board[r][c] != 0):
            continue
        val = random.randint(1,9)
        if not is_vaild(board,r,c,val):
            continue
        board[r][c] = val
        i+=1
    return board
def user_input_board():
    board = create_empty_board()
    print_board(board)
    print("start inputting your own board :)")
    while True:
        r, c, val = map(int, input("enter row , col , val : ").split())
        if r==-1:
            return board
        if not is_vaild(board, r, c, val):
            print("error : current input invalid, retry")
            continue
        board[r][c] = val
        print_board(board)
        

def create_empty_board():
    return[[0 for _ in range(9)] for _ in range(9)]
    
def is_vaild(board , r, c, val):
    if any(board[r][x] == val for x in range(9)):
        return False
    if any(board[x][c] == val for x in range(9)):
        return False
    sr = (r//3) * 3
    sc = (c//3) * 3
    for i in range(3):
        for j in range(3):
            if board[sr+i][sc+j] == val:
                return False
    return True 
def print_board(board):
    for r in range(9):
        if r % 3 == 0 and r != 0:
            print("-" * 21)  

        for c in range(9):
            if c % 3 == 0 and c != 0:
                print("|", end=" ")

            print(board[r][c] if board[r][c] != 0 else ".", end=" ")

        print()  

def count_cells(board):
    cells = 0
    for row in board:
        for element in row:
            if element!=0:
                cells+=1
    return cells
def create_board(mode):
    if mode == 1:
        difficulty = input('please select difficulty : ')
        board = generate_board(difficulty)
    elif mode ==2:
        board = user_input_board()
    else:
        print('error unknown mode selected')
        exit(-1)
    return board
if __name__ == "__main__":
    board = create_board(1)
    print("generated board : ")
    print_board(board)