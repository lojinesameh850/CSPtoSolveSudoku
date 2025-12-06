import random
from collections import deque

class Variable:
    def __init__(self, row, col, val=0):
        self.row = row
        self.col = col
        self.val = val

        if val == 0:
            self.domain = [x for x in range(1, 10)]
        else:
            self.domain = [val]

        self.neighbors = set()

    def remove_from_domain(self, val):
        if val in self.domain:
            self.domain.remove(val)

    def add_neighbor(self, xj):
        self.neighbors.add(xj)

class Constraint:
    def __init__(self, xi, xj):
        self.xi = xi
        self.xj = xj
        xi.add_neighbor(xj)

    def resolve(self):
        removed = False
        for val in self.xi.domain[:]:
            if not any(val != other for other in self.xj.domain):
                self.xi.domain.remove(val)
                removed = True
        return removed



def create_empty_board():
    return [[0 for _ in range(9)] for _ in range(9)]


def is_valid(board, r, c, val):
    if (val == 0):
        return True
    if any(board[r][x] == val for x in range(9)):
        return False
    if any(board[x][c] == val for x in range(9)):
        return False

    sr = (r // 3) * 3
    sc = (c // 3) * 3
    for i in range(3):
        for j in range(3):
            if board[sr + i][sc + j] == val:
                return False
    return True


def generate_board(difficulty):
    clue_counts = {
        "easy": 45,
        "intermediate": 33,
        "hard": 17
    }
    clues = clue_counts[difficulty]

    board = create_empty_board()

    def fill_board():
        for r in range(9):
            for c in range(9):
                if board[r][c] == 0:
                    numbers = list(range(1, 10))
                    random.shuffle(numbers)
                    for val in numbers:
                        if is_valid(board, r, c, val):
                            board[r][c] = val
                            if fill_board():
                                return True
                            board[r][c] = 0
                    return False
        return True  

    fill_board()

    cells_to_remove = 81 - clues
    while cells_to_remove > 0:
        r = random.randint(0, 8)
        c = random.randint(0, 8)
        if board[r][c] != 0:
            board[r][c] = 0
            cells_to_remove -= 1

    return board


def user_input_board():
    board = create_empty_board()
    print_board(board)
    print("Start inputting your own board :)")
    
    while True:
        r, c, val = map(int, input("enter row , col , val (-1 to finish): ").split())
        
        if r == -1:
            return board
        
        if not is_valid(board, r, c, val):
            print("Error: current input invalid, retry")
            continue

        board[r][c] = val
        print_board(board)



def print_board(board):
    for r in range(9):
        if r % 3 == 0 and r != 0:
            print("-" * 21)

        for c in range(9):
            if c % 3 == 0 and c != 0:
                print("|", end=" ")

            print(board[r][c] if board[r][c] != 0 else ".", end=" ")

        print()


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


def resolve_constraints(constraints):
    queue = deque(constraints)

    while queue:
        con = queue.popleft()

        if con.resolve():  
            
            if not con.xi.domain:
                print("Domain wipe-out occurred, puzzle invalid.")
                return False

            for neighbor in con.xi.neighbors:
                if neighbor != con.xj:
                    queue.append(Constraint(neighbor, con.xi))

    return True

def create_board(mode):
    if mode == 1:
        difficulty = input("please select difficulty : ")
        return generate_board(difficulty)
    elif mode == 2:
        return user_input_board()
    else:
        print("error unknown mode selected")
        exit(-1)


if __name__ == "__main__":
    board = create_board(2)
    print("generated board : ")
    print_board(board)

    variables, constraints = build_csp_problem(board)

    print("\nbefore resolving constraints:")
    print_variables(variables)

    if not resolve_constraints(constraints):
        print("board is invalid")

    print("\nafter resolving constraints:")
    print_variables(variables)
