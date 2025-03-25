from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from rubik import RubikCube
from algorithms.search import BFS, DFS, AStar, IDAStar, BidirectionalSearch, BeamSearch
from algorithms.other import GeneticAlgorithm, MonteCarloTreeSearch
from algorithms.advanced import KociembaAlgorithm, ThistlethwaiteAlgorithm
from worker import SolverWorker
from thread_manager import thread_manager
from rubik_state import RubikState, SOLVED_STATE, apply_move, MOVE_NAMES
from algorithms.solver import solve_rubik
import rubik_converter

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
        
        # Tăng khoảng cách giữa các button
        scroll_layout.setSpacing(8)
        
        for algo in algorithms:
            btn = QPushButton(algo)
            btn.setObjectName(algo)  # Set object name for identification
            btn.setToolTip(algo)
            # Tăng kích thước font chữ và chiều cao cho button
            font = btn.font()
            font.setPointSize(10)
            btn.setFont(font)
            btn.setMinimumHeight(36)  # Tăng chiều cao button
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
        font = self.solution_text.font()
        font.setPointSize(11)  # Tăng kích thước font
        self.solution_text.setFont(font)
        self.solution_text.setMinimumHeight(120)  # Tăng chiều cao để hiển thị nhiều nội dung hơn
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
        # Tăng cỡ chữ cho labels
        for i in range(metrics_layout.count()):
            widget = metrics_layout.itemAt(i).widget()
            if isinstance(widget, QLabel):
                font = widget.font()
                font.setPointSize(10)
                widget.setFont(font)
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
        font = self.info_text.font()
        font.setPointSize(11)  # Tăng kích thước font
        self.info_text.setFont(font)
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
        main_layout.setSpacing(12)  # Tăng khoảng cách giữa các phần tử
        
        # Input moves group
        moves_group = QGroupBox("Input Moves")
        moves_layout = QVBoxLayout()
        self.moves_input = QLineEdit()
        self.moves_input.setPlaceholderText("Enter moves (e.g. R U R' U')")
        # Tăng kích thước font và chiều cao cho input
        font = self.moves_input.font()
        font.setPointSize(11)
        self.moves_input.setFont(font)
        self.moves_input.setMinimumHeight(32)
        moves_layout.addWidget(self.moves_input)
        moves_group.setLayout(moves_layout)
        main_layout.addWidget(moves_group)

        # Control buttons
        buttons_layout = QHBoxLayout()
        reset_btn = QPushButton("Reset")
        shuffle_btn = QPushButton("Shuffle")
        # Tăng kích thước font và chiều cao cho các button
        for btn in [reset_btn, shuffle_btn]:
            font = btn.font()
            font.setPointSize(11)
            btn.setFont(font)
            btn.setMinimumHeight(36)
        buttons_layout.addWidget(reset_btn)
        buttons_layout.addWidget(shuffle_btn)
        main_layout.addLayout(buttons_layout)

        # Create tab widget for algorithm groups
        tabs = QTabWidget()
        # Tăng kích thước font cho tabs
        font = tabs.font()
        font.setPointSize(10)
        tabs.setFont(font)
        
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
            ],
            # Cập nhật tab cho thuật toán sử dụng biểu diễn hoán vị và định hướng
            "State Based": [
                "A* State-Based", "IDA* State-Based", 
                "Bidirectional State-Based", "Pattern Database"
            ]
        }
        
        # Add groups to tabs
        for group_name, algorithms in algorithm_groups.items():
            group = AlgorithmGroup(group_name, algorithms)
            # Connect group's signal to our slot
            group.buttonClicked.connect(self.on_algorithm_clicked)
            tabs.addTab(group, group_name)
        
        main_layout.addWidget(tabs)
        
        # Thêm checkbox để chọn biểu diễn
        self.use_state_representation = QCheckBox("Use state-based representation")
        self.use_state_representation.setToolTip("Use permutation and orientation to represent Rubik's cube state")
        # Tăng kích thước font cho checkbox
        font = self.use_state_representation.font()
        font.setPointSize(11)
        self.use_state_representation.setFont(font)
        main_layout.addWidget(self.use_state_representation)
        
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
            self.rubik_widget.rotate_face(face, clockwise)
            self.rubik_widget.move_queue = moves[1:]
        self.moves_input.clear()

    def parse_moves(self, moves_str):
        """Parse input string into list of moves"""
        moves = []
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
        self.rubik_widget.reset()

    def shuffle_cube(self):
        self.rubik_widget.scramble()

    def on_algorithm_clicked(self, algo_name):
        # Nếu đang chạy một thuật toán, hủy nó trước khi bắt đầu thuật toán mới
        if hasattr(self, 'worker') and self.worker is not None:
            self.cancel_solving()
            
        if not self.result_panel:
            return

        # Show system info
        from thread_manager import ThreadManager
        self.result_panel.add_result(
            f"System: {ThreadManager.TOTAL_CORES} CPU cores available\n"
            f"UI reserved cores: {ThreadManager.UI_CORES}\n"
            f"Computation cores: {ThreadManager.NUM_CORES}\n"
            f"Active threads: {thread_manager.active_thread_count}\n"
        )

        # Xóa kết quả cũ khi bắt đầu thuật toán mới
        self.result_panel.clear_results()

        # Kiểm tra xem có sử dụng biểu diễn hoán vị và định hướng không
        use_state = self.use_state_representation.isChecked()
        
        # Nếu sử dụng biểu diễn state và thuật toán là state-based
        state_based_algorithms = [
            "A* State-Based", "IDA* State-Based", 
            "Bidirectional State-Based", "Pattern Database"
        ]
        
        if use_state and algo_name in state_based_algorithms:
            self.solve_with_state(algo_name)
            return

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
                # Tăng kích thước font và chiều cao cho cancel button
                font = self.cancel_btn.font()
                font.setPointSize(11)
                self.cancel_btn.setFont(font)
                self.cancel_btn.setMinimumHeight(36)
                self.layout().addWidget(self.cancel_btn)
            self.cancel_btn.show()
            
            # Add to thread pool
            thread_manager.start_task(self.worker)
    
    def solve_with_state(self, algo_name):
        """Giải Rubik sử dụng biểu diễn hoán vị và định hướng"""
        # Lấy MainWindow để truy cập RubikState
        main_window = self.window()
        
        # Thử chuyển đổi từ biểu diễn 3D sang biểu diễn state
        try:
            rubik_state = rubik_converter.cube_to_state(self.rubik_widget.cube)
            
            # Xác định thuật toán dựa trên tên
            algorithm_map = {
                "A* State-Based": "a_star",
                "IDA* State-Based": "ida_star",
                "Bidirectional State-Based": "bidirectional",
                "Pattern Database": "pattern_database"
            }
            algorithm = algorithm_map.get(algo_name, "a_star")
            
            # Hiển thị thông báo
            self.result_panel.add_result(f"Solving with {algo_name}...")
            self.result_panel.set_algorithm(algo_name)
            
            # Tạo worker để chạy trong thread riêng
            self.worker = SolverWorker(None)
            
            # Tạo một đối tượng callable để truyền vào SolverWorker
            def solve_function():
                # Đối với Bidirectional, giới hạn độ sâu để đảm bảo hiệu suất
                if algorithm == "bidirectional":
                    max_depth = 8
                else:
                    max_depth = 20
                return solve_rubik(rubik_state, algorithm=algorithm, max_depth=max_depth, time_limit=60)
            
            # Set callable function
            self.worker.set_callable(solve_function)
            
            # Connect worker signals
            self.worker.signals.progress.connect(self.result_panel.set_progress)
            self.worker.signals.status.connect(self.result_panel.add_result)
            self.worker.signals.finished.connect(self.handle_state_solution)
            self.worker.signals.error.connect(self.handle_error)
            
            # Thêm cancel button
            if not hasattr(self, 'cancel_btn'):
                self.cancel_btn = QPushButton("Cancel")
                self.cancel_btn.clicked.connect(self.cancel_solving)
                # Tăng kích thước font và chiều cao cho cancel button
                font = self.cancel_btn.font()
                font.setPointSize(11)
                self.cancel_btn.setFont(font)
                self.cancel_btn.setMinimumHeight(36)
                self.layout().addWidget(self.cancel_btn)
            self.cancel_btn.show()
            
            # Add to thread pool
            thread_manager.start_task(self.worker)
            
        except Exception as e:
            self.result_panel.add_result(f"Error: {str(e)}")

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
        
        # Cleanup
        self.cleanup_worker()
    
    def handle_state_solution(self, result, time_taken):
        if result and result.get("solution"):
            solution = result["solution"]
            solution_str = " ".join(solution)
            nodes = result["nodes_explored"]
            depth = result["depth"]
            algorithm = result.get("algorithm", "unknown")
            
            # Thông tin bổ sung dựa vào thuật toán
            extra_info = ""
            if algorithm == "a_star":
                extra_info = f"Max queue size: {result.get('max_queue_size', 'N/A')}"
            elif algorithm == "ida_star":
                extra_info = f"Final f-limit: {result.get('final_f_limit', 'N/A')}"
            elif algorithm == "bidirectional":
                extra_info = (f"Forward states: {result.get('forward_states', 'N/A')}, "
                             f"Backward states: {result.get('backward_states', 'N/A')}")
            
            # Cập nhật kết quả
            self.result_panel.update_results(
                solution_str,
                time_taken,
                f"Nodes explored: {nodes}"
            )
            
            # Cập nhật thông tin thuật toán
            algo_names = {
                "a_star": "A* State-Based",
                "ida_star": "IDA* State-Based",
                "bidirectional": "Bidirectional State-Based",
                "pattern_database": "Pattern Database"
            }
            algo_name = algo_names.get(algorithm, algorithm)
            
            self.result_panel.update_info(
                f"<h3>{algo_name}</h3>\n\n"
                f"<p><b>Description:</b><br>Using permutation and orientation representation</p>\n\n"
                f"<p><b>Nodes explored:</b> {nodes}</p>\n"
                f"<p><b>Execution time:</b> {time_taken:.3f} seconds</p>\n"
                f"<p><b>Solution depth:</b> {depth}</p>\n"
                f"<p><b>Solution length:</b> {len(solution)} moves</p>\n"
                f"<p><b>{extra_info}</b></p>"
            )
            
            # Áp dụng các nước đi
            for move in solution:
                face = move[0]
                clockwise = not ("'" in move)
                self.rubik_widget.rotate_face(face, clockwise)
        else:
            self.result_panel.add_result("No solution found.")
        
        # Cleanup
        self.cleanup_worker()

    def handle_error(self, error_msg):
        if self.result_panel:
            self.result_panel.add_result(f"Error: {error_msg}")
        self.cleanup_worker()

    def cancel_solving(self):
        if hasattr(self, 'worker'):
            self.worker.cancel()
            self.result_panel.add_result("Solving cancelled.")
            self.cleanup_worker()

    def cleanup_worker(self):
        if hasattr(self, 'worker'):
            self.worker = None
        if hasattr(self, 'cancel_btn'):
            self.cancel_btn.hide()
