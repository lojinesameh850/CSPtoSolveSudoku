from PyQt6 import QtWidgets, QtGui, QtCore
import sys, random
from problemGenerator import generate_board , Constraint , Variable, build_csp_problem
from collections import deque


def solve_sudoku(variables, constraints):
    steps = []
    board_history = []  # <-- Store board states

    def select_unassigned_var(variables):
        unassigned = [v for row in variables for v in row if v.val == 0]
        if not unassigned:
            return None
        return min(unassigned, key=lambda v: len(v.domain))

    def ac3_after_assignment(var):
        queue = deque([Constraint(var, neighbor) for neighbor in var.neighbors])
        while queue:
            con = queue.popleft()
            if con.resolve():
                if not con.xi.domain:
                    return False
                for neighbor in con.xi.neighbors:
                    if neighbor != con.xj:
                        queue.append(Constraint(neighbor, con.xi))
        return True

    def record_board():
        board_snapshot = [[variables[r][c].val for c in range(9)] for r in range(9)]
        board_history.append(board_snapshot)

    from collections import deque

def solve_sudoku(variables, constraints):
    steps = []
    board_history = [] 

    def select_unassigned_var(variables):
        # Flatten the board to find unassigned vars
        unassigned = [v for row in variables for v in row if v.val == 0]
        if not unassigned:
            return None
        # MRV Heuristic: Minimum Remaining Values
        return min(unassigned, key=lambda v: len(v.domain))

    def ac3_after_assignment(var):
        # Queue starts with immediate neighbors constraints
        queue = deque([Constraint(var, neighbor) for neighbor in var.neighbors])
        
        while queue:
            con = queue.popleft()
            if con.resolve(): # If domain of con.xi was reduced
                if not con.xi.domain:
                    return False # Domain Wipeout found
                
                # PROPAGATION: Add neighbors of the modified variable to queue
                for neighbor in con.xi.neighbors:
                    if neighbor != con.xj:
                        queue.append(Constraint(neighbor, con.xi))
        return True

    def record_board():
        board_snapshot = [[variables[r][c].val for c in range(9)] for r in range(9)]
        board_history.append(board_snapshot)

    def backtrack():
        var = select_unassigned_var(variables)
        if var is None:
            record_board()
            return True  
        
        local_domain_backup = {}
        for r in range(9):
            for c in range(9):
                v_obj = variables[r][c]
                local_domain_backup[v_obj] = v_obj.domain[:]

        sorted_domain = sorted(var.domain) 
        
        for val in sorted_domain:
            var.val = val
            # var.domain = [val] # Constrain domain to assignment
            
            steps.append(f"Assign X{var.row}{var.col} = {val}")
            record_board()

            # Run AC-3
            # If AC-3 succeeds (no domain wipeout), continue deeper
            if ac3_after_assignment(var):
                if backtrack():
                    var.domain = [val]
                    return True

            # --- BACKTRACKING HAPPENS HERE ---
            
            steps.append(f"Backtrack X{var.row}{var.col} from {val}")
            
            # 2. FULL RESTORE: Reset the variable and restore ALL domains
            var.val = 0 
            
            # Restore the state of the whole board to what it was 
            # before we tried this value
            for r in range(9):
                for c in range(9):
                    v_obj = variables[r][c]
                    v_obj.domain = local_domain_backup[v_obj][:]
            
            record_board()

        return False

    # Initial AC-3 check (optional but recommended before starting)
    # For now, we just jump into backtrack as per your logic
    success = backtrack()
    
    if success:
        solved_board = [[variables[r][c].val for c in range(9)] for r in range(9)]
        return solved_board, steps, board_history
    else:
        return None, steps, board_history


# Sudoku Cell Widget
PASTEL_BG = "#f5f5f5"
PASTEL_BOARD_BG = "#e5e5e5" 
PASTEL_FIXED = "#e0f2f1"
PASTEL_ERROR = "#ffcdd2"  
PASTEL_VALID = "#c8e6c9"  
PASTEL_ACCENT = "#80cbc4" 

class SudokuCell(QtWidgets.QLineEdit):
    def __init__(self, fixed=False):
        super().__init__()
        self.fixed = fixed
        self.setFixedSize(50, 50) 
        self.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.setFont(QtGui.QFont("Arial", 20))
        self.reset_style()
        if fixed:
            self.setReadOnly(True)
        self.setMaxLength(1)
    def highlight_error(self):
        self.setStyleSheet(f"background:{PASTEL_ERROR}; color:#d32f2f; border:1px solid #d32f2f; border-radius:3px; font-weight:bold;")

    def highlight_valid(self):
        self.setStyleSheet(f"background:{PASTEL_VALID}; color:#388e3c; border:1px solid #388e3c; border-radius:3px; font-weight:bold;")

    def reset_style(self):
        if self.fixed:
            self.setStyleSheet(f"background:{PASTEL_FIXED}; color:#111; border:1px solid #777; border-radius:3px; font-weight:bold;")
        else:
            self.setStyleSheet(f"background:#ffffff; color:#333; border:1px solid #aaa; border-radius:3px; font-weight:normal;")

class SudokuGame(QtWidgets.QWidget):
    restart_signal = QtCore.pyqtSignal()

    def __init__(self, mode, difficulty):
        super().__init__()
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet(f"background:{PASTEL_BG}; color:#333;")
        self.mode = mode
        self.difficulty = difficulty
        self.cells = []
        self.grid_layout = None
        self.board_history = []
        self.history_index = 0
        
        if self.mode == 0:
            self.puzzle = generate_board(self.difficulty)
            self.editable = False
        else:
            self.puzzle = [[0]*9 for _ in range(9)]
            self.editable = True
        self.build_ui()

    def build_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        
        layout.addStretch() 

        self.grid_layout = QtWidgets.QGridLayout()
        self.grid_layout.setSpacing(0)
        self.grid_layout.setContentsMargins(0, 0, 0, 0)
        self.build_board()
        
        board_container = QtWidgets.QWidget()
        board_container.setLayout(self.grid_layout)
        board_container.setStyleSheet(f"""
            QWidget {{
                background:{PASTEL_BOARD_BG}; 
                border:4px solid #333;
                padding: 15px; /* Increased padding from 10px to 15px */
            }}
        """)
        
        h_center_board = QtWidgets.QHBoxLayout()
        h_center_board.addStretch()
        h_center_board.addWidget(board_container)
        h_center_board.addStretch()
        
        layout.addLayout(h_center_board)
        layout.addSpacing(30) 

        btns = QtWidgets.QHBoxLayout()

        button_style = f"""
            QPushButton {{
                background:{PASTEL_ACCENT}; 
                color:white; 
                padding:12px 25px;
                font-size:16px;
                border-radius:8px;
                border: none;
                min-width: 120px;
            }}
            QPushButton:hover {{
                background:#66bb6a;
            }}
        """

        solve_btn = QtWidgets.QPushButton("Solve")
        solve_btn.clicked.connect(self.solve)
        solve_btn.setStyleSheet(button_style)

        restart_btn = QtWidgets.QPushButton("Restart Game")
        restart_btn.clicked.connect(self.restart_signal.emit)
        restart_btn.setStyleSheet(button_style)

        btns.addWidget(solve_btn)
        btns.addSpacing(20)
        btns.addWidget(restart_btn)

        btn_container = QtWidgets.QWidget()
        btn_container.setLayout(btns)
        
        h_center_btns = QtWidgets.QHBoxLayout()
        h_center_btns.addStretch()
        h_center_btns.addWidget(btn_container)
        h_center_btns.addStretch()
        
        layout.addLayout(h_center_btns)
        
        layout.addStretch() 
        history_layout = QtWidgets.QHBoxLayout()
        self.prev_btn = QtWidgets.QPushButton("Previous")
        self.next_btn = QtWidgets.QPushButton("Next")
        self.prev_btn.clicked.connect(self.show_prev_board)
        self.next_btn.clicked.connect(self.show_next_board)
        self.prev_btn.setEnabled(False)
        self.next_btn.setEnabled(False)
        history_layout.addWidget(self.prev_btn)
        history_layout.addWidget(self.next_btn)
        layout.addLayout(history_layout)
    def show_board(self, board):
        for r in range(9):
            for c in range(9):
                val = board[r][c]
                cell = self.cells[r][c]
                if val == 0:
                    cell.setText("")
                else:
                    cell.setText(str(val))
                cell.reset_style()

    def show_prev_board(self):
        if self.history_index > 0:
            self.history_index -= 1
            self.show_board(self.board_history[self.history_index])
        self.update_history_buttons()

    def show_next_board(self):
        if self.history_index < len(self.board_history) - 1:
            self.history_index += 1
            self.show_board(self.board_history[self.history_index])
        self.update_history_buttons()

    def update_history_buttons(self):
        self.prev_btn.setEnabled(self.history_index > 0)
        self.next_btn.setEnabled(self.history_index < len(self.board_history) - 1)

    def build_board(self):
        self.cells = []
        for r in range(9):
            row = []
            for c in range(9):
                val = self.puzzle[r][c]
                fixed = (val != 0 and not self.editable)
                cell = SudokuCell(fixed=fixed)

                if val:
                    cell.setText(str(val))
                else:
                    if not fixed:
                        cell.textChanged.connect(lambda text, rr=r, cc=c: self.validate(rr, cc))

                top = 2 if r % 3 == 0 else 1
                left = 2 if c % 3 == 0 else 1
                
                right = 1 if c != 8 and (c+1) % 3 != 0 else 2 if (c+1) % 3 == 0 else 1
                bottom = 1 if r != 8 and (r+1) % 3 != 0 else 2 if (r+1) % 3 == 0 else 1
                
                thick_border = "#333"
                light_border = "#999"

                cell.setStyleSheet(cell.styleSheet() +
                    f"border-top:{top}px solid {thick_border if top == 2 else light_border};"
                    f"border-left:{left}px solid {thick_border if left == 2 else light_border};"
                    f"border-right:{right}px solid {thick_border if right == 2 else light_border};"
                    f"border-bottom:{bottom}px solid {thick_border if bottom == 2 else light_border};"
                    f"margin:0px;") 

                if r == 0:
                    cell.setStyleSheet(cell.styleSheet().replace(f"border-top:{top}px", "border-top:0px"))
                if c == 0:
                    cell.setStyleSheet(cell.styleSheet().replace(f"border-left:{left}px", "border-left:0px"))
                if r == 8:
                    cell.setStyleSheet(cell.styleSheet().replace(f"border-bottom:{bottom}px", "border-bottom:0px"))
                if c == 8:
                    cell.setStyleSheet(cell.styleSheet().replace(f"border-right:{right}px", "border-right:0px"))
                    
                self.grid_layout.addWidget(cell, r, c)
                row.append(cell)
            self.cells.append(row)

    # Validation Logic
    def validate(self, r, c):
        cell = self.cells[r][c]
        val = cell.text().strip()

        cell.reset_style()
        # Empty cell
        if not val:
            return
        # Must be digit 1-9
        if not val.isdigit() or not (1 <= int(val) <= 9):
            cell.highlight_error(); return
        # Must be unique in row, col, 3×3 subgrid
        for cc in range(9):
            if cc != c and self.cells[r][cc].text() == val:
                cell.highlight_error(); return
        for rr in range(9):
            if rr != r and self.cells[rr][c].text() == val:
                cell.highlight_error(); return
        sr, sc = (r//3)*3, (c//3)*3
        for rr in range(sr, sr+3):
            for cc in range(sc, sc+3):
                if (rr,cc)!=(r,c) and self.cells[rr][cc].text()==val:
                    cell.highlight_error(); return

        cell.highlight_valid()

    # Solve board
    def solve(self):
        board = []
        for r in range(9):
            row = []
            for c in range(9):
                t = self.cells[r][c].text()
                row.append(int(t) if t.isdigit() else 0)
            board.append(row)

        self.variables, self.constraints = build_csp_problem(board)
        solved, steps, history = solve_sudoku(self.variables, self.constraints)
        self.board_history = history
        self.history_index = len(history)-1
        self.update_history_buttons()

        if solved is None:
            QtWidgets.QMessageBox.information(self,"Unsolvable","No solution exists.")
            return

        self.show_board(solved)


# Start Menu
class StartMenu(QtWidgets.QWidget):
    start_signal = QtCore.pyqtSignal(int, str)

    def __init__(self):
        super().__init__()
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet(f"background:{PASTEL_BG}; color:#333;")

        outer_layout = QtWidgets.QVBoxLayout(self)
        outer_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        menu_layout = QtWidgets.QVBoxLayout()

        title = QtWidgets.QLabel("Sudoku CSP")
        title.setFont(QtGui.QFont("Arial", 32, QtGui.QFont.Weight.Bold))
        title.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        component_style = f"""
            QLabel {{
                padding: 8px;
                background: {PASTEL_BG}; /* Ensure label background is main BG */
                font-size: 16px;
            }}
            QComboBox {{
                padding: 8px;
                border: 2px solid {PASTEL_ACCENT}; /* Thicker border */
                border-radius: 6px; /* Rounded corners */
                background: white; 
                font-size: 16px;
            }}
            QPushButton {{
                background:{PASTEL_ACCENT};
                color:white;
                padding:12px 25px;
                font-size:18px;
                border-radius:8px;
                border: none;
            }}
            QPushButton:hover {{
                background:#66bb6a;
            }}
        """
        self.setStyleSheet(self.styleSheet() + component_style)


        self.mode_box = QtWidgets.QComboBox()
        self.mode_box.addItems(["Mode 1 (AI generates)","Mode 2 (User input)"])

        self.diff_box = QtWidgets.QComboBox()
        self.diff_box.addItems(["Easy","Medium","Hard"])

        start_btn = QtWidgets.QPushButton("Start Game")
        start_btn.clicked.connect(lambda: self.start_signal.emit(self.mode_box.currentIndex(), self.diff_box.currentText()))

        menu_layout.addWidget(title)
        menu_layout.addSpacing(20)
        menu_layout.addWidget(QtWidgets.QLabel("Select Mode:"))
        menu_layout.addWidget(self.mode_box)
        menu_layout.addSpacing(10)
        menu_layout.addWidget(QtWidgets.QLabel("Select Difficulty:"))
        menu_layout.addWidget(self.diff_box)
        menu_layout.addSpacing(20)
        menu_layout.addWidget(start_btn)
        
        menu_container = QtWidgets.QWidget()
        menu_container.setLayout(menu_layout)
        menu_container.setMaximumWidth(350)
        
        h_center_layout = QtWidgets.QHBoxLayout()
        h_center_layout.addStretch()
        h_center_layout.addWidget(menu_container)
        h_center_layout.addStretch()

        outer_layout.addLayout(h_center_layout)


# Main Application Controller
class MainWindow(QtWidgets.QStackedWidget):
    def __init__(self):
        super().__init__()
        self.menu = StartMenu()
        self.menu.start_signal.connect(self.start_game)
        self.addWidget(self.menu)
        self.setCurrentWidget(self.menu)

    def start_game(self, mode, difficulty):
        self.game = SudokuGame(mode, difficulty)
        self.game.restart_signal.connect(self.restart)
        self.addWidget(self.game)
        self.setCurrentWidget(self.game)

    def restart(self):
        self.setCurrentWidget(self.menu)
        self.removeWidget(self.game)
        del self.game

# Application Entry Point
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    win = MainWindow()
    win.setWindowTitle("Sudoku CSP")
    win.resize(600, 750) 
    win.show()
    sys.exit(app.exec())