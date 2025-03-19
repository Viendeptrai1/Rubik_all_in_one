from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from rubik import RubikCube
from algorithms.search import BFS, DFS, AStar, IDAStar, BidirectionalSearch, BeamSearch
from algorithms.other import GeneticAlgorithm, MonteCarloTreeSearch
from algorithms.advanced import KociembaAlgorithm, ThistlethwaiteAlgorithm
from worker import SolverWorker
from thread_manager import thread_manager

class AlgorithmGroup(QGroupBox):
    buttonClicked = pyqtSignal(str)  # Add new signal
    
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
            btn.setObjectName(algo)  # Set object name for identification
            btn.setToolTip(algo)
            # Connect directly to local slot
            btn.clicked.connect(lambda checked, name=algo: self.buttonClicked.emit(name))
            scroll_layout.addWidget(btn)
        
        scroll_layout.addStretch()
        scroll_content.setLayout(scroll_layout)
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)
        self.setLayout(layout)
    
    def get_controls_widget(self):
        """Tìm ControlsWidget parent"""
        parent = self.parent()
        while parent:
            if isinstance(parent, ControlsWidget):
                return parent
            parent = parent.parent()
        return None

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
            ],
            "Advanced": [
                "Kociemba's Algorithm", "Thistlethwaite's Algorithm"
            ]
        }
        
        # Add groups to tabs
        for group_name, algorithms in algorithm_groups.items():
            group = AlgorithmGroup(group_name, algorithms)
            # Connect group's signal to our slot
            group.buttonClicked.connect(self.on_algorithm_clicked)
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
        # Pass the rubik_widget to result panel
        if self.result_panel:
            self.result_panel.set_rubik_widget(self.rubik_widget)

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
        if not self.result_panel or hasattr(self, 'worker'):
            return

        # Show system info
        from thread_manager import ThreadManager
        self.result_panel.add_result(
            f"System: {ThreadManager.TOTAL_CORES} CPU cores available\n"
            f"UI reserved cores: {ThreadManager.UI_CORES}\n"
            f"Computation cores: {ThreadManager.NUM_CORES}\n"
            f"Active threads: {thread_manager.active_thread_count}\n"
        )

        # Map algorithm names to their classes
        algorithm_map = {
            "Breadth-First Search": BFS,
            "Depth-First Search": DFS,
            "A* Search": AStar,
            "IDA*": IDAStar,
            "Bidirectional Search": BidirectionalSearch,
            "Beam Search": BeamSearch,
            "Genetic Algorithm": GeneticAlgorithm,
            "Monte Carlo Tree Search": MonteCarloTreeSearch,
            "Kociemba's Algorithm": KociembaAlgorithm,
            "Thistlethwaite's Algorithm": ThistlethwaiteAlgorithm
        }

        if algo_name in algorithm_map:
            # Create worker first without an algorithm
            self.worker = SolverWorker(None)
            
            # Create algorithm
            algorithm = algorithm_map[algo_name](self.rubik_widget.rubik)
            
            # Set algorithm in worker AFTER it's created
            self.worker.set_algorithm(algorithm)
            
            # Cập nhật UI
            self.result_panel.set_algorithm(algo_name)
            self.result_panel.clear_results()
            
            # Connect worker signals to result panel
            self.worker.signals.progress.connect(self.result_panel.set_progress)
            self.worker.signals.status.connect(self.result_panel.add_result)
            self.worker.signals.finished.connect(self.handle_solution)
            self.worker.signals.error.connect(self.handle_error)
            # Connect new metrics signal
            self.worker.signals.metrics.connect(self.result_panel.update_metrics)
            
            # Thêm cancel button
            if not hasattr(self, 'cancel_btn'):
                self.cancel_btn = QPushButton("Cancel")
                self.cancel_btn.clicked.connect(self.cancel_solving)
                self.layout().addWidget(self.cancel_btn)
            self.cancel_btn.show()
            
            # Add to thread pool
            thread_manager.start_task(self.worker)

    def handle_solution(self, solution, time_taken):
        if solution:
            # Cập nhật kết quả
            self.result_panel.update_results(
                solution,  # Pass the solution directly
                time_taken,
                self.worker.algorithm.complexity
            )
            
            # Cập nhật thông tin thuật toán vào panel bên phải
            self.result_panel.update_info(
                f"<h3>{self.worker.algorithm.__class__.__name__}</h3>\n\n"
                f"<p><b>Description:</b><br>{self.worker.algorithm.description}</p>\n\n"
                f"<p><b>Time complexity:</b> {self.worker.algorithm.complexity}</p>\n"
                f"<p><b>Execution time:</b> {time_taken:.3f} seconds</p>\n"
                f"<p><b>Solution length:</b> {len(solution)} moves</p>"
            )
            
            # Don't auto-execute moves anymore
            # Let the user decide using the step buttons
        
        # Hide progress bar
        self.result_panel.set_progress(0, 0)
        
        # Cleanup
        self.cleanup_worker()

    def handle_error(self, error_msg):
        self.result_panel.add_result(f"Error: {error_msg}")
        self.cleanup_worker()

    def cancel_solving(self):
        if hasattr(self, 'worker'):
            self.worker.cancel()
            self.cleanup_worker()

    def cleanup_worker(self):
        if hasattr(self, 'worker'):
            delattr(self, 'worker')
        if hasattr(self, 'cancel_btn'):
            self.cancel_btn.hide()
