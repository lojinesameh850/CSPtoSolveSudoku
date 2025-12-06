import random
class Variable:
    row : int
    col : int
    val : int
    domain : list
    def __init__(self, row , col, val=0 ):
        self.row = row
        self.col = col
        self.val = val
        if val ==0:
            self.domain = [x for x in range(1,10)]
        else:
            self.domain = [val]
        self.neighbors = set()
    def remove_from_domain(self,val):
        if val in self.domain:
            self.domain.remove(val)
    def add_neighbor(self,xj):
        self.neighbors.add(xj)
class Constraint:
    xi : Variable
    xj : Variable

    def __init__(self, xi, xj):
        self.xi = xi
        self.xj = xj
        self.xi.add_neighbor(xj)
        self.xj.add_neighbor(xi)
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
def build_csp_problem(board):
    variables = [[Variable(r, c, board[r][c]) for c in range(9)] for r in range(9)]
    constraints = []

    for r in range(9):
        for c in range(9):
            Xi = variables[r][c]

            for cc in range(9):
                if cc != c:
                    Xj = variables[r][cc]
                    constraints.append(Constraint(Xi, Xj))

            for rr in range(9):
                if rr != r:
                    Xj = variables[rr][c]
                    constraints.append(Constraint(Xi, Xj))

            sr = (r // 3) * 3
            sc = (c // 3) * 3
            for rr in range(sr, sr + 3):
                for cc in range(sc, sc + 3):
                    if rr != r or cc != c:
                        Xj = variables[rr][cc]
                        constraints.append(Constraint(Xi, Xj))

    return variables, constraints
def print_variables(variables):
    for r in range(9):
        for c in range(9):
            v = variables[r][c]
            print(f"X{v.row}{v.col} -> {v.domain}")
def print_constraints(constraints):
    for con in constraints:
        xi = con.xi
        xj = con.xj
        print(f"(X{xi.row}{xi.col}, X{xj.row}{xj.col})")
if __name__ == "__main__":
    board = create_board(1)
    print("generated board : ")
    print_board(board)
    variables, constraints = build_csp_problem(board)
    print_variables(variables)
    # print_constraints(constraints)
