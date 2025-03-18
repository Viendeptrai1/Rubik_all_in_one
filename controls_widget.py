from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from rubik import RubikCube


class AlgorithmGroup(QGroupBox):
    def __init__(self, title, algorithms, parent=None):
        super().__init__(title, parent)
        layout = QVBoxLayout()
        
        # Create scrollable area for algorithms
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout()
        
        for algo in algorithms:
            btn = QPushButton(algo)
            btn.setToolTip(algo)  # Show full name on hover
            scroll_layout.addWidget(btn)
        
        scroll_layout.addStretch()
        scroll_content.setLayout(scroll_layout)
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)
        self.setLayout(layout)

class ResultPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()
        
        # Tạo splitter để chia đôi panel
        splitter = QSplitter(Qt.Horizontal)
        
        # Panel trái cho kết quả giải
        left_panel = QWidget()
        left_layout = QVBoxLayout()
        
        # Kết quả giải
        solution_group = QGroupBox("Solution")
        solution_layout = QVBoxLayout()
        self.solution_text = QTextEdit()
        self.solution_text.setReadOnly(True)
        self.solution_text.setMaximumHeight(100)
        solution_layout.addWidget(self.solution_text)
        solution_group.setLayout(solution_layout)
        left_layout.addWidget(solution_group)
        
        # Thời gian và độ phức tạp
        metrics_group = QGroupBox("Metrics")
        metrics_layout = QGridLayout()
        metrics_layout.addWidget(QLabel("Time:"), 0, 0)
        self.time_label = QLabel("0.00s")
        metrics_layout.addWidget(self.time_label, 0, 1)
        metrics_layout.addWidget(QLabel("Complexity:"), 1, 0)
        self.complexity_label = QLabel("O(n)")
        metrics_layout.addWidget(self.complexity_label, 1, 1)
        metrics_group.setLayout(metrics_layout)
        left_layout.addWidget(metrics_group)
        
        left_panel.setLayout(left_layout)
        
        # Panel phải cho thông tin thuật toán
        right_panel = QWidget()
        right_layout = QVBoxLayout()
        info_group = QGroupBox("Algorithm Info")
        info_layout = QVBoxLayout()
        self.info_text = QTextEdit()
        self.info_text.setReadOnly(True)
        info_layout.addWidget(self.info_text)
        info_group.setLayout(info_layout)
        right_layout.addWidget(info_group)
        right_panel.setLayout(right_layout)
        
        # Thêm panels vào splitter
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        
        layout.addWidget(splitter)
        self.setLayout(layout)
    
    def update_results(self, solution, time, complexity):
        self.solution_text.setText(solution)
        self.time_label.setText(f"{time:.2f}s")
        self.complexity_label.setText(complexity)
    
    def update_info(self, info):
        self.info_text.setText(info)

class ControlsWidget(QWidget):
    def __init__(self, rubik_widget, parent=None):
        super().__init__(parent)
        self.rubik_widget = rubik_widget
        
        # Main layout
        main_layout = QVBoxLayout()
        
        # Input moves group
        moves_group = QGroupBox("Input Moves")
        moves_layout = QVBoxLayout()
        self.moves_input = QLineEdit()
        self.moves_input.setPlaceholderText("Enter moves (e.g. R U R' U')")
        moves_layout.addWidget(self.moves_input)
        moves_group.setLayout(moves_layout)
        main_layout.addWidget(moves_group)

        # Control buttons
        buttons_layout = QHBoxLayout()
        reset_btn = QPushButton("Reset")
        shuffle_btn = QPushButton("Shuffle")
        buttons_layout.addWidget(reset_btn)
        buttons_layout.addWidget(shuffle_btn)
        main_layout.addLayout(buttons_layout)

        # Create tab widget for algorithm groups
        tabs = QTabWidget()
        
        # Define algorithm groups - SIMPLIFIED
        algorithm_groups = {
            "Search": [
                "Breadth-First Search", "Depth-First Search", 
                "A* Search", "IDA*",
                "Bidirectional Search", "Beam Search"
            ],
            "Other": [
                "Genetic Algorithm", "Monte Carlo Tree Search"
            ]
        }
        
        # Add groups to tabs
        for group_name, algorithms in algorithm_groups.items():
            group = AlgorithmGroup(group_name, algorithms)
            tabs.addTab(group, group_name)
        
        main_layout.addWidget(tabs)
        
        # Add result panel
        self.result_panel = None  # Sẽ được set sau
        
        self.setLayout(main_layout)

        # Connect signals
        self.moves_input.returnPressed.connect(self.apply_moves)
        reset_btn.clicked.connect(self.reset_cube)
        shuffle_btn.clicked.connect(self.shuffle_cube)

    def set_result_panel(self, panel):
        self.result_panel = panel

    def apply_moves(self):
        moves = self.parse_moves(self.moves_input.text())
        if moves:
            face, clockwise = moves[0]
            self.rubik_widget.rubik.rotate_face(face, clockwise)
            self.rubik_widget.move_queue = moves[1:]
        self.moves_input.clear()

    def parse_moves(self, moves_str):
        """Parse input string into list of moves"""
        moves = []
        i = 0
        # Loại bỏ khoảng trắng thừa và chuyển sang chữ hoa
        moves_str = moves_str.strip().upper()
        tokens = moves_str.split()
        
        for token in tokens:
            if len(token) == 0:
                continue
                
            if token[0] not in 'UDLRFB':
                continue
                
            face = token[0]
            clockwise = True
            
            # Kiểm tra dấu '
            if len(token) > 1 and token[1] == "'":
                clockwise = False
            
            moves.append((face, clockwise))
            
        return moves

    def reset_cube(self):
        if hasattr(self.rubik_widget.rubik, '_scramble_queue'):
            self.rubik_widget.rubik._scramble_queue = []
        self.rubik_widget.rubik = RubikCube()
        self.rubik_widget.update()

    def shuffle_cube(self):
        self.rubik_widget.rubik.scramble()
        self.rubik_widget.update()

    def on_algorithm_clicked(self, algo_name):
        if not self.result_panel:
            return
        """Handle algorithm button clicks"""
        # Placeholder algorithm info - you'll need to fill this with real data
        algorithm_info = {
            "Breadth-First Search": {
                "info": "BFS is a graph traversal algorithm that explores all vertices at the present depth before moving on to vertices at the next depth level.",
                "complexity": "O(b^d)",
                "details": "- Complete: Yes\n- Optimal: Yes (with uniform cost)\n- Space complexity: O(b^d)"
            },
            # Add more algorithm information here
        }
        
        if algo_name in algorithm_info:
            info = algorithm_info[algo_name]
            # TODO: Implement actual solving logic here
            self.result_panel.update_results(
                "R U R' U'",  # Placeholder solution
                0.05,  # Placeholder time
                info["complexity"]
            )
            self.result_panel.update_info(
                f"{algo_name}\n\n{info['info']}\n\n{info['details']}"
            )

    def on_algorithm_selected(self, name):
        """Handle algorithm selection"""
        if self.result_panel:
            self.result_panel.set_algorithm(name)
            self.result_panel.add_result(f"Selected algorithm: {name}")
            self.result_panel.add_result("This is a placeholder. Actual implementation coming soon.")
            # Placeholder for algorithm execution
            pass
