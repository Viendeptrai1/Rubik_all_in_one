from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from rubik_3x3 import RubikCube
from rubik_2x2 import RubikCube2x2
import time
import random
import pandas as pd
import os
import openpyxl
from RubikState.rubik_solver import (
    a_star, bfs, dfs, ucs, ids, ida_star, greedy_best_first, 
    hill_climbing_max, hill_climbing_random, pdb_astar, simple_hill_climbing,
    # Thêm các thuật toán mới
    simulated_annealing, genetic_algorithm, local_beam_search,
    and_or_graph_search, belief_states_search, ac3_search,
    backtracking_search_strategy1, backtracking_search_strategy2
)
from RubikState.rubik_deepcube import DeepCubeSolver
# Import thêm solver PDB 2x2 và DeepCubeA 2x2
from rubik_2x2_pdb_solver import PDBSolver
from rubik_2x2_ai import DeepCube2x2Solver

# Tạo Worker Thread để chạy thuật toán giải trong luồng riêng biệt
class SolverThread(QThread):
    # Định nghĩa các tín hiệu để giao tiếp với UI
    solution_found = pyqtSignal(list, int, float, dict)  # path, nodes_visited, time_taken, stats
    progress_update = pyqtSignal(int, int, dict)  # nodes_visited, elapsed_time, current_stats
    error_occurred = pyqtSignal(str)  # error message
    solver_finished = pyqtSignal(bool)  # success flag
    
    def __init__(self, algorithm_func, current_state, time_limit):
        super().__init__()
        self.algorithm_func = algorithm_func
        self.current_state = current_state
        self.time_limit = time_limit
        self.running = False
    
    def run(self):
        self.running = True
        start_time = time.time()
        try:
            # Đối với các thuật toán hiện tại - cập nhật để nhận stats
            result = self.algorithm_func(self.current_state, time_limit=self.time_limit, return_stats=True)
            
            # Kiểm tra nếu đã bị hủy
            if not self.running:
                return
            
            # Kiểm tra định dạng kết quả - nếu có stats thì sử dụng, nếu không thì tạo dict trống
            if len(result) == 4:  # Định dạng mới (path, nodes_visited, time_taken, stats)
                path, nodes_visited, time_taken, stats = result
            else:  # Định dạng cũ (path, nodes_visited, time_taken)
                path, nodes_visited, time_taken = result
                stats = {}  # Dict trống cho các thuật toán cũ chưa cập nhật
                
            if path:
                self.solution_found.emit(path, nodes_visited, time_taken, stats)
            else:
                self.solver_finished.emit(False)
                
        except Exception as e:
            if self.running:
                self.error_occurred.emit(str(e))
        finally:
            self.running = False
    
    def stop(self):
        self.running = False
        self.wait()

class ControlsWidget(QWidget):
    def __init__(self, rubik_widget):
        super().__init__()
        # Đối tượng Rubik 3D (dạng hình)
        self.rubik_widget = rubik_widget
        
        # Xác định loại khối Rubik (2x2 hoặc 3x3)
        self.is_2x2 = isinstance(rubik_widget.cube, RubikCube2x2)
            
        self.init_ui()

    def set_rubik_widget(self, rubik_widget):
        """Cập nhật widget rubik hiện tại khi chuyển tab"""
        # Cập nhật widget Rubik 3D (dạng hình)
        self.rubik_widget = rubik_widget
        
        # Cập nhật trạng thái nút theo widget mới
        self.update_buttons()
        
        # Xác định loại khối Rubik mới
        self.is_2x2 = isinstance(rubik_widget.cube, RubikCube2x2)
        
        # Cập nhật hiển thị trạng thái
        self.update_state_display()

    def update_buttons(self):
        """Cập nhật trạng thái nút dựa trên widget hiện tại"""
        pass

    def init_ui(self):
        # Main layout
        main_layout = QVBoxLayout()
        
        # ==== TẠO BỐ CỤC 3 PHẦN ====
        
        # ----- PHẦN TRÊN: Thanh ngang chia 2 panel trái và phải -----
        top_splitter = QSplitter(Qt.Horizontal)
        
        # -- PHẦN TRÊN TRÁI: ĐIỀU KHIỂN CƠ BẢN --
        top_left_widget = QWidget()
        top_left_layout = QVBoxLayout()
        top_left_widget.setLayout(top_left_layout)
        
        # Đặt tiêu đề
        top_left_layout.addWidget(QLabel("<b>Điều khiển cơ bản</b>"))
        
        # Input moves group
        top_left_layout.addWidget(QLabel("Nhập nước đi:"))
        moves_input = QLineEdit()
        moves_input.setPlaceholderText("Ví dụ: R U R' U' F R U F' U'")
        self.moves_input = moves_input
        self.moves_input.returnPressed.connect(self.apply_moves)
        top_left_layout.addWidget(moves_input)
        
        apply_btn = QPushButton("Áp dụng")
        apply_btn.clicked.connect(self.apply_moves)
        top_left_layout.addWidget(apply_btn)
        
        # Control buttons
        buttons_layout = QHBoxLayout()
        reset_btn = QPushButton("Reset Rubik")
        reset_btn.clicked.connect(self.reset_cube)
        top_left_layout.addLayout(buttons_layout)
        buttons_layout.addWidget(reset_btn)
        
        # Tạo nhóm nút radio cho độ khó xáo trộn
        shuffle_group = QGroupBox("Xáo trộn")
        shuffle_layout = QVBoxLayout()
        
        # Tạo layout ngang cho nút xáo trộn và các radio button
        shuffle_options_layout = QHBoxLayout()
        
        # Tạo nút xáo trộn
        shuffle_btn = QPushButton("Xáo trộn")
        shuffle_btn.clicked.connect(self.shuffle_cube)
        shuffle_options_layout.addWidget(shuffle_btn)
        
        # Tạo radio buttons cho các mức độ khó
        self.difficulty_group = QButtonGroup(self)
        
        # Radio button cho mức dễ
        self.easy_radio = QRadioButton("Dễ")
        self.easy_radio.setToolTip("2-3 bước")
        self.difficulty_group.addButton(self.easy_radio, 0)
        shuffle_options_layout.addWidget(self.easy_radio)
        
        # Radio button cho mức trung bình
        self.medium_radio = QRadioButton("TB")
        self.medium_radio.setToolTip("4-6 bước")
        self.difficulty_group.addButton(self.medium_radio, 1)
        shuffle_options_layout.addWidget(self.medium_radio)
        
        # Radio button cho mức khó
        self.hard_radio = QRadioButton("Khó")
        self.hard_radio.setToolTip("7-10 bước")
        self.difficulty_group.addButton(self.hard_radio, 2)
        shuffle_options_layout.addWidget(self.hard_radio)
        
        # Mặc định chọn mức trung bình
        self.medium_radio.setChecked(True)
        
        shuffle_layout.addLayout(shuffle_options_layout)
        shuffle_group.setLayout(shuffle_layout)
        top_left_layout.addWidget(shuffle_group)
        
        # Lời giải
        solution_group = QGroupBox("Lời giải")
        solution_layout = QVBoxLayout()
        
        self.solution_moves = QTextEdit()
        self.solution_moves.setReadOnly(True)
        self.solution_moves.setFixedHeight(80)
        solution_layout.addWidget(self.solution_moves)
        
        # Create a horizontal layout for buttons
        solution_buttons_layout = QHBoxLayout()
        
        apply_solution_btn = QPushButton("Áp dụng lời giải")
        apply_solution_btn.clicked.connect(self.apply_solution)
        solution_buttons_layout.addWidget(apply_solution_btn)
        
        export_btn = QPushButton("Export")
        export_btn.clicked.connect(self.export_solution)
        solution_buttons_layout.addWidget(export_btn)
        
        solution_layout.addLayout(solution_buttons_layout)
        
        solution_group.setLayout(solution_layout)
        top_left_layout.addWidget(solution_group)
        
        # -- PHẦN TRÊN PHẢI: THÔNG TIN RUBIK --
        top_right_widget = QWidget()
        top_right_layout = QVBoxLayout()
        top_right_widget.setLayout(top_right_layout)
        
        # Đặt tiêu đề
        top_right_layout.addWidget(QLabel("<b>Thông tin Rubik</b>"))
        
        # TextEdit để hiển thị trạng thái
        self.state_display = QTextEdit()
        self.state_display.setReadOnly(True)
        top_right_layout.addWidget(self.state_display)
        
        # Thêm top left và top right vào top splitter
        top_splitter.addWidget(top_left_widget)
        top_splitter.addWidget(top_right_widget)
        
        # Đặt tỷ lệ phân chia phần trên (1:3)
        top_splitter.setSizes([300, 700])
        
        # ----- PHẦN DƯỚI: THUẬT TOÁN VÀ KẾT QUẢ -----
        bottom_widget = QWidget()
        bottom_layout = QVBoxLayout()
        bottom_widget.setLayout(bottom_layout)
        
        # === TABS THUẬT TOÁN ===
        algo_tabs = QTabWidget()
        
        # Tạo button group cho các radio button
        self.algorithm_button_group = QButtonGroup(self)
        
        # --- Tab 1: Thuật toán không thông tin ---
        uninformed_tab = QWidget()
        uninformed_layout = QVBoxLayout(uninformed_tab)
        
        # Radio buttons
        self.bfs_radio = QRadioButton("Breadth-First Search (BFS)")
        self.dfs_radio = QRadioButton("Depth-First Search (DFS)")
        self.ucs_radio = QRadioButton("Uniform Cost Search (UCS)")
        self.ids_radio = QRadioButton("Iterative Deepening Search (IDS)")
        
        # Thêm vào button group
        self.algorithm_button_group.addButton(self.bfs_radio, 0)
        self.algorithm_button_group.addButton(self.dfs_radio, 1)
        self.algorithm_button_group.addButton(self.ucs_radio, 2)
        self.algorithm_button_group.addButton(self.ids_radio, 3)
        
        # Mặc định chọn BFS
        self.bfs_radio.setChecked(True)
        
        # Thêm vào layout
        uninformed_layout.addWidget(self.bfs_radio)
        uninformed_layout.addWidget(self.dfs_radio)
        uninformed_layout.addWidget(self.ucs_radio)
        uninformed_layout.addWidget(self.ids_radio)
        uninformed_layout.addStretch()
        
        # --- Tab 2: Thuật toán có thông tin ---
        informed_tab = QWidget()
        informed_layout = QVBoxLayout(informed_tab)
        
        # Radio buttons
        self.astar_radio = QRadioButton("A* Search")
        self.idastar_radio = QRadioButton("IDA* Search")
        self.greedy_radio = QRadioButton("Greedy Best-First Search")
        
        # Thêm vào button group
        self.algorithm_button_group.addButton(self.astar_radio, 4)
        self.algorithm_button_group.addButton(self.idastar_radio, 5)
        self.algorithm_button_group.addButton(self.greedy_radio, 6)
        
        # Thêm vào layout
        informed_layout.addWidget(self.astar_radio)
        informed_layout.addWidget(self.idastar_radio)
        informed_layout.addWidget(self.greedy_radio)
        informed_layout.addStretch()
        
        # --- Tab 3: Thuật toán tìm kiếm cục bộ ---
        local_tab = QWidget()
        local_layout = QVBoxLayout(local_tab)
        
        # Radio buttons
        self.hill_climbing_max_radio = QRadioButton("Steepest Ascent Hill Climbing")
        self.hill_climbing_random_radio = QRadioButton("Stochastic Hill Climbing")
        self.simple_hill_climbing_radio = QRadioButton("Simple Hill Climbing")
        self.simulated_annealing_radio = QRadioButton("Simulated Annealing")
        self.genetic_algorithm_radio = QRadioButton("Genetic Algorithm")
        self.local_beam_search_radio = QRadioButton("Local Beam Search")
        
        # Thêm vào button group
        self.algorithm_button_group.addButton(self.hill_climbing_max_radio, 7)
        self.algorithm_button_group.addButton(self.hill_climbing_random_radio, 8)
        self.algorithm_button_group.addButton(self.simple_hill_climbing_radio, 9)
        self.algorithm_button_group.addButton(self.simulated_annealing_radio, 11)
        self.algorithm_button_group.addButton(self.genetic_algorithm_radio, 12)
        self.algorithm_button_group.addButton(self.local_beam_search_radio, 13)
        
        # Thêm vào layout
        local_layout.addWidget(self.hill_climbing_max_radio)
        local_layout.addWidget(self.hill_climbing_random_radio)
        local_layout.addWidget(self.simple_hill_climbing_radio)
        local_layout.addWidget(self.simulated_annealing_radio)
        local_layout.addWidget(self.genetic_algorithm_radio)
        local_layout.addWidget(self.local_beam_search_radio)
        local_layout.addStretch()
        
        # --- Tab 4: Tìm kiếm trong môi trường phức tạp ---
        complex_tab = QWidget()
        complex_layout = QVBoxLayout(complex_tab)
        
        # Radio buttons
        self.and_or_search_radio = QRadioButton("AND-OR Graph Search")
        self.belief_states_radio = QRadioButton("Belief States")
        
        # Thêm vào button group
        self.algorithm_button_group.addButton(self.and_or_search_radio, 14)
        self.algorithm_button_group.addButton(self.belief_states_radio, 15)
        
        # Thêm vào layout
        complex_layout.addWidget(self.and_or_search_radio)
        complex_layout.addWidget(self.belief_states_radio)
        complex_layout.addStretch()
        
        # --- Tab 5: RL (Reinforcement Learning) ---
        rl_tab = QWidget()
        rl_layout = QVBoxLayout(rl_tab)
        
        # Radio buttons
        self.rl_dqn_radio = QRadioButton("DeepCubeA (3x3)")
        self.rl_pdb_2x2_radio = QRadioButton("Pattern Database (2x2)")
        self.rl_deepcube_2x2_radio = QRadioButton("DeepCubeA (2x2)")
        
        # Thêm vào button group
        self.algorithm_button_group.addButton(self.rl_dqn_radio, 10)
        self.algorithm_button_group.addButton(self.rl_pdb_2x2_radio, 19)
        self.algorithm_button_group.addButton(self.rl_deepcube_2x2_radio, 20)
        
        # Thêm vào layout
        rl_layout.addWidget(self.rl_dqn_radio)
        rl_layout.addWidget(self.rl_pdb_2x2_radio)
        rl_layout.addWidget(self.rl_deepcube_2x2_radio)
        rl_layout.addStretch()
        
        # Thêm các tab vào tabwidget
        algo_tabs.addTab(uninformed_tab, "Uninformed Search")
        algo_tabs.addTab(informed_tab, "Informed Search")
        algo_tabs.addTab(local_tab, "Local Search")
        algo_tabs.addTab(complex_tab, "Complex Environment")
        algo_tabs.addTab(rl_tab, "Reinforcement Learning")
        
        # Cài đặt thời gian
        time_layout = QHBoxLayout()
        time_layout.addWidget(QLabel("Time limit (seconds):"))
        self.time_limit_spin = QSpinBox()
        self.time_limit_spin.setRange(1, 300)
        self.time_limit_spin.setValue(120)
        time_layout.addWidget(self.time_limit_spin)
        time_layout.addStretch()
        
        # Nút giải Rubik
        solve_btn = QPushButton("Solve Rubik's Cube")
        solve_btn.clicked.connect(self.solve_rubik)
        time_layout.addWidget(solve_btn)
        
        # Layout cho nút so sánh thuật toán
        compare_layout = QHBoxLayout()
        compare_layout.addStretch()
        
        # Nút so sánh các thuật toán
        compare_btn = QPushButton("Compare Algorithms")
        compare_btn.clicked.connect(self.compare_algorithms)
        compare_btn.setToolTip("So sánh hiệu suất của các thuật toán trên trạng thái Rubik hiện tại")
        compare_layout.addWidget(compare_btn)
        
        # Thêm vào layout dưới
        bottom_layout.addWidget(algo_tabs)
        bottom_layout.addLayout(time_layout)
        bottom_layout.addLayout(compare_layout)
        
        # === KẾT QUẢ GIẢI ===
        result_group = QGroupBox("Solution Results")
        result_layout = QVBoxLayout()
        
        # Hiển thị trạng thái giải
        status_layout = QHBoxLayout()
        status_layout.addWidget(QLabel("Status:"))
        self.solution_status = QLabel("Ready")
        self.solution_status.setStyleSheet("font-weight: bold;")
        status_layout.addWidget(self.solution_status)
        result_layout.addLayout(status_layout)
        
        # Thống kê cơ bản
        stats_layout = QGridLayout()
        stats_layout.addWidget(QLabel("Time:"), 0, 0)
        self.solution_time = QLabel("0 seconds")
        stats_layout.addWidget(self.solution_time, 0, 1)
        
        stats_layout.addWidget(QLabel("Nodes visited:"), 0, 2)
        self.nodes_visited = QLabel("0")
        stats_layout.addWidget(self.nodes_visited, 0, 3)
        
        stats_layout.addWidget(QLabel("Solution length:"), 1, 0)
        self.solution_length = QLabel("0")
        stats_layout.addWidget(self.solution_length, 1, 1)
        
        stats_layout.addWidget(QLabel("Memory usage:"), 1, 2)
        self.memory_usage = QLabel("0 states")
        stats_layout.addWidget(self.memory_usage, 1, 3)
        
        stats_layout.addWidget(QLabel("Branching factor:"), 2, 0)
        self.branching_factor = QLabel("0")
        stats_layout.addWidget(self.branching_factor, 2, 1)
        
        stats_layout.addWidget(QLabel("Pruning ratio:"), 2, 2)
        self.pruning_ratio = QLabel("0%")
        stats_layout.addWidget(self.pruning_ratio, 2, 3)
        
        result_layout.addLayout(stats_layout)
        
        # Phân tích chi tiết tabs
        analysis_tabs = QTabWidget()
        
        # Tab thống kê
        stats_tab = QWidget()
        stats_layout = QVBoxLayout(stats_tab)
        self.detailed_stats = QTextEdit()
        self.detailed_stats.setReadOnly(True)
        stats_layout.addWidget(self.detailed_stats)
        
        # Tab heuristic
        heuristic_tab = QWidget()
        heuristic_layout = QVBoxLayout(heuristic_tab)
        self.heuristic_stats = QTextEdit()
        self.heuristic_stats.setReadOnly(True)
        heuristic_layout.addWidget(self.heuristic_stats)
        
        # Thêm tabs
        analysis_tabs.addTab(stats_tab, "Detailed Statistics")
        analysis_tabs.addTab(heuristic_tab, "Heuristic Analysis")
        
        result_layout.addWidget(analysis_tabs)
        result_group.setLayout(result_layout)
        
        # Thêm kết quả giải vào layout dưới
        bottom_layout.addWidget(result_group)
        
        # ----- TẠO SPLITTER TỔNG THỂ ĐỂ CHIA PHẦN TRÊN VÀ DƯỚI -----
        main_splitter = QSplitter(Qt.Vertical)
        main_splitter.addWidget(top_splitter)
        main_splitter.addWidget(bottom_widget)
        
        # Đặt tỷ lệ phân chia (40% trên, 60% dưới)
        main_splitter.setSizes([400, 600])
        
        # Thêm main splitter vào layout chính
        main_layout.addWidget(main_splitter)
        
        self.setLayout(main_layout)
        
        # Lưu trữ lời giải hiện tại
        self.current_solution = []
        
        # Cập nhật hiển thị trạng thái ban đầu
        self.update_state_display()
    
    def update_state_display(self):
        """Cập nhật hiển thị trạng thái Rubik"""
        # Xóa nội dung cũ
        self.state_display.clear()
        
        # Lấy trạng thái Rubik hiện tại
        try:
            # Lấy trạng thái từ đối tượng Rubik
            state_tuple = self.rubik_widget.rubik.get_state_tuple()
            
            if self.is_2x2:
                # Rubik 2x2: (cp, co)
                cp, co = state_tuple
                
                # Format chuỗi hiển thị
                text = "Rubik 2x2 State:\n\n"
                text += "Corner Permutation (cp):\n"
                text += f"{cp}\n\n"
                text += "Corner Orientation (co):\n"
                text += f"{co}\n"
            else:
                # Rubik 3x3: (cp, co, ep, eo)
                cp, co, ep, eo = state_tuple
                
                # Format chuỗi hiển thị
                text = "Rubik 3x3 State:\n\n"
                text += "Corner Permutation (cp):\n"
                text += f"{cp}\n\n"
                text += "Corner Orientation (co):\n"
                text += f"{co}\n\n"
                text += "Edge Permutation (ep):\n"
                text += f"{ep}\n\n"
                text += "Edge Orientation (eo):\n"
                text += f"{eo}\n"
            
            # Hiển thị trong TextEdit
            self.state_display.setPlainText(text)
        except Exception as e:
            self.state_display.setPlainText(f"Lỗi khi lấy trạng thái: {str(e)}")
    
    def apply_moves(self):
        """Áp dụng các bước di chuyển từ input"""
        moves_str = self.moves_input.text()
        if not moves_str:
            return
            
        moves = self.parse_moves(moves_str)
        if not moves:
            return
            
        # Áp dụng các nước đi cho biểu diễn dạng hình (Rubik 3D)
        self.apply_moves_to_3d_cube(moves)
            
        # Xóa nội dung input sau khi áp dụng
        self.moves_input.clear()
    
    def apply_moves_to_3d_cube(self, moves):
        """Áp dụng các nước đi cho biểu diễn dạng hình (Rubik 3D)"""
        # Thêm các nước đi vào hàng đợi của widget Rubik
        self.rubik_widget.move_queue.extend(moves)
        
        # Nếu không có animation đang chạy, bắt đầu nước đi đầu tiên
        if not self.rubik_widget.rubik.animating and self.rubik_widget.move_queue:
            face, clockwise = self.rubik_widget.move_queue.pop(0)
            self.rubik_widget.rubik.rotate_face(face, clockwise)
    
    def parse_moves(self, moves_str):
        """Chuyển đổi chuỗi moves thành list (face, clockwise)"""
        moves = []
        # Xử lý trường hợp không có khoảng trắng
        if ' ' not in moves_str:
            # Ghép các ký tự liên tiếp
            i = 0
            while i < len(moves_str):
                if i < len(moves_str) and moves_str[i].upper() in 'FLUDRB':
                    face = moves_str[i].upper()
                    clockwise = True
                    
                    # Kiểm tra ký tự tiếp theo
                    if i + 1 < len(moves_str):
                        # Xử lý case R'
                        if moves_str[i + 1] == "'":
                            clockwise = False
                            i += 1  # Bỏ qua ký tự '
                        # Xử lý case R2 - quay 180 độ = quay 2 lần
                        elif moves_str[i + 1] == "2":
                            # Thêm 2 lần quay cùng hướng
                            moves.append((face, clockwise))
                            moves.append((face, clockwise))
                            i += 1  # Bỏ qua số 2
                            i += 1  # Đi tiếp
                            continue
                    
                    moves.append((face, clockwise))
                i += 1
        else:
            # Xử lý theo khoảng trắng như cũ
            tokens = moves_str.split()
            
            for token in tokens:
                if not token:
                    continue
                    
                face = token[0].upper()
                
                if face not in 'FLUDRB':
                    continue
                    
                # Xử lý case R2
                if len(token) > 1 and token[1] == "2":
                    # Thêm 2 lần quay cùng chiều
                    moves.append((face, True))
                    moves.append((face, True))
                # Xử lý case R'
                elif len(token) > 1 and token[1] == "'":
                    moves.append((face, False))
                # Xử lý case R
                else:
                    moves.append((face, True))
                    
        return moves
    
    def reset_cube(self):
        """Reset khối Rubik về trạng thái đã giải"""
        # Reset biểu diễn dạng hình (Rubik 3D)
        if isinstance(self.rubik_widget.rubik, RubikCube2x2):
            self.rubik_widget.rubik = RubikCube2x2()
            self.rubik_widget.cube = self.rubik_widget.rubik
        else:
            self.rubik_widget.rubik = RubikCube()
            self.rubik_widget.cube = self.rubik_widget.rubik
        
        # Xóa hàng đợi nước đi nếu có
        self.rubik_widget.move_queue.clear()
        
        # Reset thông tin lời giải
        self.solution_status.setText("Ready")
        self.solution_time.setText("0 seconds")
        self.nodes_visited.setText("0")
        self.solution_length.setText("0")
        self.solution_moves.clear()
        self.current_solution = []
        
        # Cập nhật hiển thị trạng thái
        self.update_state_display()
    
    def shuffle_cube(self):
        """Xáo trộn Rubik"""
        # Tránh xáo trộn khi đang animation
        if self.rubik_widget.rubik.animating or self.rubik_widget.move_queue:
            self.solution_status.setText("Không thể xáo trộn khi đang thực hiện animation")
            return
        
        # Xác định số bước dựa trên mức độ khó đã chọn
        selected_difficulty = self.difficulty_group.checkedId()
        
        if selected_difficulty == 0:  # Dễ (2-3 bước)
            num_moves = random.randint(2, 3)
            difficulty_text = "Dễ"
        elif selected_difficulty == 1:  # Trung bình (4-6 bước)
            num_moves = random.randint(4, 6)
            difficulty_text = "Trung bình"
        elif selected_difficulty == 2:  # Khó (7-10 bước)
            num_moves = random.randint(7, 10)
            difficulty_text = "Khó"
        else:  # Mặc định (4-6 bước)
            num_moves = random.randint(4, 6)
            difficulty_text = "Trung bình"
        
        # Sinh ngẫu nhiên nước đi theo số bước đã xác định
        available_moves = ["U", "D", "F", "B", "L", "R"]
        variants = ["", "'", "2"]
        
        # Tạo chuỗi nước đi
        move_strings = []
        for _ in range(num_moves):
            move = random.choice(available_moves)
            variant = random.choice(variants)
            move_strings.append(move + variant)
        
        # Tạo chuỗi để hiển thị
        display_moves_str = " ".join(move_strings)
        
        # Parse và áp dụng nước đi
        moves = self.parse_moves(display_moves_str)
        self.apply_moves_to_3d_cube(moves)
        
        # Cập nhật hiển thị trạng thái
        self.update_state_display()
        
        # Thông báo
        self.solution_status.setText(f"Đã xáo trộn (Độ khó: {difficulty_text}, {num_moves} bước): {display_moves_str}")
    
    def get_current_state(self):
        """Lấy trạng thái hiện tại của Rubik để sử dụng cho thuật toán giải"""
        try:
            # Tránh lấy trạng thái khi đang animation
            if self.rubik_widget.rubik.animating or self.rubik_widget.move_queue:
                self.solution_status.setText("Không thể giải khi đang thực hiện animation")
                return None
                
            # Lấy trạng thái từ đối tượng Rubik 3D
            from RubikState.rubik_chen import RubikState
            from RubikState.rubik_2x2 import Rubik2x2State
            
            # Tạo trạng thái từ state_tuple
            if self.is_2x2:
                cp, co = self.rubik_widget.rubik.state_tuple
                current_state = Rubik2x2State(cp, co)
            else:
                cp, co, ep, eo = self.rubik_widget.rubik.state_tuple
                current_state = RubikState(cp, co, ep, eo)
                
            return current_state
        except Exception as e:
            self.solution_status.setText(f"Lỗi khi lấy trạng thái: {str(e)}")
            print(f"Lỗi khi lấy trạng thái: {e}")
            return None
            
    def solve_rubik(self):
        """
        Giải Rubik dựa trên thuật toán đã chọn
        """
        try:
            # Lấy trạng thái Rubik hiện tại
            current_state = self.get_current_state()
            
            if current_state is None:
                self.solution_status.setText("Không thể lấy trạng thái Rubik hiện tại!")
                return
            
            # Lấy thuật toán đã chọn từ radio buttons
            selected_id = self.algorithm_button_group.checkedId()
            algorithm_registry = self.get_algorithm_registry()
            
            if selected_id not in algorithm_registry:
                self.solution_status.setText("Thuật toán không hợp lệ!")
                return
                
            # Lấy tên hiển thị và tên thuật toán từ registry
            algorithm_display_name, algorithm_name = algorithm_registry[selected_id]
            
            # Ánh xạ tên thuật toán với hàm
            algorithm_funcs = {
                "bfs": bfs,
                "dfs": dfs,
                "ucs": ucs,
                "ids": ids,
                "a_star": a_star,
                "ida_star": ida_star,
                "greedy_best_first": greedy_best_first,
                "hill_climbing_max": hill_climbing_max,
                "hill_climbing_random": hill_climbing_random,
                "simple_hill_climbing": simple_hill_climbing,
                "pdb_astar": pdb_astar,
                "deepcube": lambda state, time_limit, return_stats: DeepCubeSolver().solve(state),
                "pdb_2x2": lambda state, time_limit, return_stats: 
                    self.wrap_pdb_2x2_solver(state, time_limit),
                "deepcube_2x2": lambda state, time_limit, return_stats: 
                    self.wrap_deepcube_2x2_solver(state, time_limit),
                "simulated_annealing": simulated_annealing,
                "genetic_algorithm": genetic_algorithm,
                "local_beam_search": local_beam_search,
                "and_or_search": and_or_graph_search,
                "belief_states": belief_states_search,
                "ac3": ac3_search,
                "backtracking_1": backtracking_search_strategy1,
                "backtracking_2": backtracking_search_strategy2,
            }
            
            if algorithm_name not in algorithm_funcs or algorithm_funcs[algorithm_name] is None:
                self.solution_status.setText(f"Thuật toán {algorithm_display_name} chưa được triển khai!")
                return
            
            # Lấy thời gian giới hạn
            time_limit = 30  # Mặc định
            if hasattr(self, 'time_limit_spin'):
                time_limit = self.time_limit_spin.value()
            
            # Cập nhật UI
            self.solution_status.setText(f"Đang giải với thuật toán {algorithm_display_name}...")
            self.solution_time.setText("0 seconds")
            self.nodes_visited.setText("0")
            self.solution_length.setText("0")
            self.memory_usage.setText("0 states")
            self.branching_factor.setText("0")
            self.pruning_ratio.setText("0%")
            self.detailed_stats.setPlainText("")
            self.heuristic_stats.setPlainText("")
            self.solution_moves.setPlainText("")
            
            # Tạo và hiển thị thanh tiến trình
            if not hasattr(self, 'progress_bar'):
                self.progress_bar = QProgressBar()
                self.progress_bar.setRange(0, 0)  # Chế độ hoạt động liên tục
                
                # Tìm layout thích hợp để thêm thanh tiến trình
                options_layout = None
                
                for layout in self.findChildren(QHBoxLayout):
                    for i in range(layout.count()):
                        item = layout.itemAt(i)
                        if item.widget() and isinstance(item.widget(), QPushButton) and item.widget().text() == "Solve Rubik's Cube":
                            options_layout = layout
                            break
                
                if options_layout:
                    options_layout.insertWidget(0, self.progress_bar)
                else:
                    # Nếu không tìm thấy, thêm vào layout chính
                    self.layout().addWidget(self.progress_bar)
                    
            self.progress_bar.setVisible(True)
            
            # Tạo nút hủy nếu chưa có
            if not hasattr(self, 'cancel_btn'):
                self.cancel_btn = QPushButton("Hủy")
                self.cancel_btn.clicked.connect(self.cancel_solving)
                
                # Tìm layout thích hợp để thêm nút hủy
                options_layout = None
                
                for layout in self.findChildren(QHBoxLayout):
                    for i in range(layout.count()):
                        item = layout.itemAt(i)
                        if item.widget() and isinstance(item.widget(), QPushButton) and item.widget().text() == "Solve Rubik's Cube":
                            options_layout = layout
                            break
                
                # Nếu không tìm thấy, thử cách khác
                if not options_layout:
                    for layout in self.findChildren(QHBoxLayout):
                        has_spin = False
                        has_solve_btn = False
                        for i in range(layout.count()):
                            widget = layout.itemAt(i).widget()
                            if isinstance(widget, QSpinBox):
                                has_spin = True
                            elif isinstance(widget, QPushButton) and widget.text() == "Solve Rubik's Cube":
                                has_solve_btn = True
                        if has_spin and has_solve_btn:
                            options_layout = layout
                            break
                
                # Nếu tìm thấy options_layout, thêm nút hủy
                if options_layout:
                    options_layout.insertWidget(options_layout.count()-1, self.cancel_btn)
                else:
                    # Thêm vào layout chính nếu không tìm thấy
                    self.layout().addWidget(self.cancel_btn)
            
            self.cancel_btn.setVisible(True)
            
            # Khởi động thread
            self.solver_thread = SolverThread(algorithm_funcs[algorithm_name], current_state, time_limit)
            
            # Kết nối tín hiệu
            self.solver_thread.solution_found.connect(self.on_solution_found)
            self.solver_thread.progress_update.connect(self.on_progress_update)
            self.solver_thread.error_occurred.connect(self.on_solver_error)
            self.solver_thread.solver_finished.connect(self.on_solver_finished)
            
            # Khởi động thread
            self.solver_thread.start()
            
            # Bắt đầu timer để cập nhật thanh tiến trình
            if not hasattr(self, 'progress_timer'):
                self.progress_timer = QTimer()
                self.progress_timer.timeout.connect(self.update_progress)
            
            self.progress_start_time = time.time()
            self.progress_timer.start(100)  # Cập nhật mỗi 100ms
            
        except Exception as e:
            self.solution_status.setText(f"Lỗi: {str(e)}")
            if hasattr(self, 'progress_bar'):
                self.progress_bar.setVisible(False)
            print(f"Lỗi khi giải Rubik: {e}")
    
    def get_algorithm_registry(self):
        """Đăng ký thuật toán - dễ dàng mở rộng trong tương lai"""
        return {
            0: ("BFS", "bfs"),
            1: ("DFS", "dfs"),
            2: ("UCS", "ucs"),
            3: ("IDS", "ids"),
            4: ("A*", "a_star"),
            5: ("IDA*", "ida_star"),
            6: ("Greedy Best-First", "greedy_best_first"),
            7: ("Hill Climbing Max", "hill_climbing_max"),
            8: ("Hill Climbing Random", "hill_climbing_random"),
            9: ("Simple Hill Climbing", "simple_hill_climbing"),
            10: ("Pattern Database A*", "pdb_astar"),
            11: ("Simulated Annealing", "simulated_annealing"),
            12: ("Genetic Algorithm", "genetic_algorithm"),
            13: ("Local Beam Search", "local_beam_search"),
            14: ("AND-OR Graph Search", "and_or_search"),
            15: ("Belief States", "belief_states"),
            16: ("AC-3", "ac3"),
            17: ("Backtracking Search (Gán giá trị từng biến)", "backtracking_1"),
            18: ("Backtracking Search (Kiểm tra ràng buộc sớm)", "backtracking_2"),
            19: ("Pattern Database (2x2)", "pdb_2x2"),
            20: ("DeepCubeA (2x2)", "deepcube_2x2")
        }
    
    def update_progress(self):
        """Cập nhật thông tin tiến độ"""
        elapsed = time.time() - self.progress_start_time
        self.solution_time.setText(f"{elapsed:.1f} seconds")

    def on_solution_found(self, path, nodes_visited, time_taken, stats):
        """Xử lý khi tìm thấy lời giải"""
        # Dừng timer
        if hasattr(self, 'progress_timer') and self.progress_timer.isActive():
            self.progress_timer.stop()
        
        # Ẩn thanh tiến trình và nút hủy
        if hasattr(self, 'progress_bar'):
            self.progress_bar.setVisible(False)
        if hasattr(self, 'cancel_btn'):
            self.cancel_btn.setVisible(False)
        
        # Cập nhật UI cơ bản
        self.solution_status.setText("Đã tìm thấy lời giải!")
        self.solution_time.setText(f"{time_taken:.2f} seconds")
        self.nodes_visited.setText(f"{nodes_visited}")
        self.solution_length.setText(f"{len(path)}")
        
        # Cập nhật các thông số phân tích mới
        if 'memory_used' in stats:
            self.memory_usage.setText(f"{stats['memory_used']} states")
        else:
            self.memory_usage.setText("Không có dữ liệu")
            
        if 'effective_branching' in stats:
            self.branching_factor.setText(f"{stats['effective_branching']:.2f}")
        else:
            self.branching_factor.setText("Không có dữ liệu")
            
        if 'pruning_ratio' in stats:
            self.pruning_ratio.setText(f"{stats['pruning_ratio']:.2f}%")
        else:
            self.pruning_ratio.setText("Không có dữ liệu")
        
        # Hiển thị thống kê chi tiết
        detailed_text = "Thống kê chi tiết:\n"
        for key, value in stats.items():
            if key not in ['memory_used', 'effective_branching', 'pruning_ratio']:
                if isinstance(value, float):
                    detailed_text += f"- {key}: {value:.4f}\n"
                else:
                    detailed_text += f"- {key}: {value}\n"
        self.detailed_stats.setPlainText(detailed_text)
        
        # Hiển thị thống kê heuristic
        if 'heuristic_accuracy' in stats or 'heuristic_stats' in stats:
            heuristic_text = "Phân tích heuristic:\n"
            if 'heuristic_accuracy' in stats:
                heuristic_text += f"- Độ chính xác: {stats['heuristic_accuracy']:.2f}%\n"
            
            if 'heuristic_stats' in stats and isinstance(stats['heuristic_stats'], dict):
                for key, value in stats['heuristic_stats'].items():
                    heuristic_text += f"- {key}: {value}\n"
            
            self.heuristic_stats.setPlainText(heuristic_text)
        else:
            self.heuristic_stats.setPlainText("Không có dữ liệu phân tích heuristic.")
        
        # Hiển thị lời giải
        moves_str = " ".join([move if move.find("'") > 0 else f"{move} " for move in path])
        self.solution_moves.setPlainText(moves_str)
        
        # Lưu lời giải để áp dụng sau
        self.current_solution = self.parse_moves(moves_str)

    def on_progress_update(self, nodes_visited, elapsed_time, current_stats):
        """Cập nhật thông tin tiến độ từ thread"""
        self.nodes_visited.setText(f"{nodes_visited}")
        self.solution_time.setText(f"{elapsed_time:.1f} seconds")
        
        # Cập nhật các thông số phân tích nếu có
        if 'memory_used' in current_stats:
            self.memory_usage.setText(f"{current_stats['memory_used']} states")
            
        if 'effective_branching' in current_stats:
            self.branching_factor.setText(f"{current_stats['effective_branching']:.2f}")
            
        if 'pruning_ratio' in current_stats:
            self.pruning_ratio.setText(f"{current_stats['pruning_ratio']:.2f}%")

    def on_solver_error(self, error_message):
        """Xử lý khi có lỗi trong quá trình giải"""
        # Dừng timer
        if hasattr(self, 'progress_timer') and self.progress_timer.isActive():
            self.progress_timer.stop()
        
        # Ẩn thanh tiến trình và nút hủy
        if hasattr(self, 'progress_bar'):
            self.progress_bar.setVisible(False)
        if hasattr(self, 'cancel_btn'):
            self.cancel_btn.setVisible(False)
        
        self.solution_status.setText(f"Lỗi: {error_message}")

    def on_solver_finished(self, success):
        """Xử lý khi giải xong nhưng không tìm thấy lời giải"""
        # Dừng timer
        if hasattr(self, 'progress_timer') and self.progress_timer.isActive():
            self.progress_timer.stop()
        
        # Ẩn thanh tiến trình và nút hủy
        if hasattr(self, 'progress_bar'):
            self.progress_bar.setVisible(False)
        if hasattr(self, 'cancel_btn'):
            self.cancel_btn.setVisible(False)
        
        if not success:
            self.solution_status.setText("Không tìm thấy lời giải trong giới hạn thời gian!")

    def cancel_solving(self):
        """Hủy quá trình giải"""
        if hasattr(self, 'solver_thread') and self.solver_thread.isRunning():
            self.solver_thread.stop()
            
        # Dừng timer
        if hasattr(self, 'progress_timer') and self.progress_timer.isActive():
            self.progress_timer.stop()
        
        # Ẩn thanh tiến trình và nút hủy
        if hasattr(self, 'progress_bar'):
            self.progress_bar.setVisible(False)
        if hasattr(self, 'cancel_btn'):
            self.cancel_btn.setVisible(False)
        
        self.solution_status.setText("Đã hủy quá trình giải")
    
    def apply_solution(self):
        # Gỡ lỗi
        print("Áp dụng lời giải:", self.current_solution)
        
        if not self.current_solution:
            self.solution_status.setText("Chưa có lời giải để áp dụng!")
            return
            
        # Áp dụng lời giải cho Rubik 3D
        self.apply_moves_to_3d_cube(self.current_solution)

    def wrap_pdb_2x2_solver(self, state, time_limit):
        """Wrapper để chuyển đổi kết quả từ PDBSolver sang định dạng tương thích"""
        try:
            # Bắt đầu đo thời gian
            start_time = time.time()
            
            # Gọi solver
            pdb_solver = PDBSolver()
            solution = pdb_solver.solve(state, time_limit=time_limit)
            
            # Nếu tìm thấy lời giải
            if solution:
                # Thời gian giải
                solve_time = time.time() - start_time
                
                # Tạo stats dict - lấy từ PDBSolver nếu có, hoặc tạo rỗng
                stats = getattr(pdb_solver, 'stats', {})
                if not stats:
                    stats = {'memory_used': 0, 'effective_branching': 0, 'pruning_ratio': 0}
                
                # Lấy số nodes đã duyệt
                nodes_visited = getattr(pdb_solver, 'nodes_expanded', 0)
                if not nodes_visited:
                    nodes_visited = 0
                
                return solution, nodes_visited, solve_time, stats
            else:
                # Không tìm thấy lời giải
                return None, 0, time.time() - start_time, {}
        except Exception as e:
            print(f"Lỗi khi sử dụng PDBSolver: {str(e)}")
            return None, 0, 0, {}
    
    def wrap_deepcube_2x2_solver(self, state, time_limit):
        """Wrapper để chuyển đổi kết quả từ DeepCube2x2Solver sang định dạng tương thích"""
        try:
            # Bắt đầu đo thời gian
            start_time = time.time()
            
            # Gọi solver
            solver = DeepCube2x2Solver()
            solver.load_model()  # Đảm bảo model đã được load
            solution = solver.solve(state)
            
            # Nếu tìm thấy lời giải
            if solution:
                # Thời gian giải
                solve_time = time.time() - start_time
                
                # Tạo stats dict
                stats = {
                    'memory_used': getattr(solver, 'nodes_expanded', 0),
                    'effective_branching': 0,
                    'pruning_ratio': 0,
                    'algorithm': 'DeepCube2x2'
                }
                
                # Lấy số nodes đã duyệt
                nodes_visited = getattr(solver, 'nodes_expanded', len(solution) * 12)  # rough estimate if not available
                
                return solution, nodes_visited, solve_time, stats
            else:
                # Không tìm thấy lời giải
                return None, 0, time.time() - start_time, {}
        except Exception as e:
            print(f"Lỗi khi sử dụng DeepCube2x2Solver: {str(e)}")
            return None, 0, 0, {}

    def export_solution(self):
        """
        Export solution steps to an Excel file with state indicators
        """
        if not hasattr(self, 'current_solution') or not self.current_solution:
            QMessageBox.warning(self, "Không có lời giải", "Vui lòng giải Rubik trước khi xuất lời giải.")
            return
        
        try:
            # Lấy trạng thái hiện tại của khối Rubik
            current_state = self.get_current_state()
            if current_state is None:
                QMessageBox.warning(self, "Lỗi", "Không thể lấy trạng thái Rubik hiện tại!")
                return
            
            # Lấy dữ liệu lời giải từ solution_moves
            solution_text = self.solution_moves.toPlainText()
            if not solution_text.strip():
                QMessageBox.warning(self, "Không có lời giải", "Không tìm thấy lời giải để xuất.")
                return
            
            # Phân tích chuỗi lời giải
            move_strings = []
            
            # Filter out any non-move text like "→" or descriptive labels
            for move in solution_text.split():
                if move and move not in ["→", "Lời", "giải:", "bước"]:
                    move_strings.append(move)
            
            if not move_strings:
                QMessageBox.warning(self, "Lỗi", "Không thể phân tích chuỗi lời giải.")
                return
            
            # Tạo tên file với timestamp
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename, _ = QFileDialog.getSaveFileName(
                self, "Lưu lời giải", f"solution_{timestamp}.xlsx", "Excel Files (*.xlsx)"
            )
            
            if not filename:
                return  # Người dùng hủy lưu
                
            # Import thư viện MOVES cho việc áp dụng nước đi
            from RubikState.rubik_2x2 import MOVES_2x2
            from RubikState.rubik_chen import MOVES_3x3
            moves_dict = MOVES_2x2 if self.is_2x2 else MOVES_3x3
            
            # Tạo dữ liệu cho file Excel - lưu trạng thái sau mỗi bước
            data = []
            
            # Lưu trạng thái ban đầu
            if self.is_2x2:
                initial_data = {
                    'STT': 0,
                    'Nước đi': 'Initial',
                    'CP (Corner Permutation)': str(current_state.cp),
                    'CO (Corner Orientation)': str(current_state.co)
                }
                data.append(initial_data)
            else:
                initial_data = {
                    'STT': 0,
                    'Nước đi': 'Initial',
                    'CP (Corner Permutation)': str(current_state.cp),
                    'CO (Corner Orientation)': str(current_state.co),
                    'EP (Edge Permutation)': str(current_state.ep),
                    'EO (Edge Orientation)': str(current_state.eo)
                }
                data.append(initial_data)
            
            # Áp dụng từng nước đi và lưu trạng thái
            state = current_state
            for i, move_str in enumerate(move_strings, 1):
                # Áp dụng nước đi vào trạng thái
                state = state.apply_move(move_str, moves_dict)
                
                # Lưu trạng thái mới
                if self.is_2x2:
                    state_data = {
                        'STT': i,
                        'Nước đi': move_str,
                        'CP (Corner Permutation)': str(state.cp),
                        'CO (Corner Orientation)': str(state.co)
                    }
                else:
                    state_data = {
                        'STT': i,
                        'Nước đi': move_str,
                        'CP (Corner Permutation)': str(state.cp),
                        'CO (Corner Orientation)': str(state.co),
                        'EP (Edge Permutation)': str(state.ep),
                        'EO (Edge Orientation)': str(state.eo)
                    }
                data.append(state_data)
            
            # Tạo DataFrame từ dữ liệu
            df = pd.DataFrame(data)
            
            # Tạo Excel writer và định dạng
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                # Write solution data
                df.to_excel(writer, sheet_name='Trạng thái Rubik', index=False)
                
                # Định dạng file sau khi ghi
                workbook = writer.book
                worksheet = writer.sheets['Trạng thái Rubik']
                
                # Số cột thay đổi tùy vào loại Rubik
                num_cols = 4 if self.is_2x2 else 6
                
                # Định dạng tiêu đề
                for col in range(1, num_cols + 1):
                    cell = worksheet.cell(row=1, column=col)
                    cell.font = openpyxl.styles.Font(bold=True)
                    cell.alignment = openpyxl.styles.Alignment(horizontal='center')
                    cell.fill = openpyxl.styles.PatternFill(start_color="FFFF00", end_color="FFFF00", fill_type="solid")
                
                # Điều chỉnh độ rộng cột
                worksheet.column_dimensions['A'].width = 5
                worksheet.column_dimensions['B'].width = 10
                worksheet.column_dimensions['C'].width = 25
                worksheet.column_dimensions['D'].width = 25
                if not self.is_2x2:
                    worksheet.column_dimensions['E'].width = 25
                    worksheet.column_dimensions['F'].width = 25
                
                # Add a summary sheet
                summary_data = {
                    'Thuộc tính': ['Loại Rubik', 'Số bước giải', 'Thuật toán sử dụng', 'Thời gian giải', 'Ghi chú'],
                    'Giá trị': [
                        '2x2' if self.is_2x2 else '3x3',
                        len(move_strings),
                        self.get_algorithm_registry()[self.algorithm_button_group.checkedId()][0],
                        self.solution_time.text(),
                        'File này chứa trạng thái của khối Rubik sau mỗi bước giải. Chỉ số CP, CO, EP, EO biểu diễn hoán vị và định hướng của các góc và cạnh.'
                    ]
                }
                summary_df = pd.DataFrame(summary_data)
                summary_df.to_excel(writer, sheet_name='Tổng quan', index=False)
                
                # Định dạng sheet tổng quan
                worksheet = writer.sheets['Tổng quan']
                worksheet.column_dimensions['A'].width = 20
                worksheet.column_dimensions['B'].width = 50
            
            QMessageBox.information(self, "Xuất thành công", f"Lời giải và trạng thái đã được xuất ra file {filename}")
            
        except Exception as e:
            QMessageBox.critical(self, "Lỗi khi xuất", f"Đã xảy ra lỗi: {str(e)}")
            print(f"Lỗi khi export: {e}")
    
    def compare_algorithms(self):
        """So sánh các thuật toán trên trạng thái Rubik hiện tại và xuất báo cáo"""
        # Lấy trạng thái Rubik hiện tại
        current_state = self.get_current_state()
        if current_state is None:
            QMessageBox.warning(self, "Lỗi", "Không thể lấy trạng thái Rubik hiện tại!")
            return
            
        # Xác định rubik là 2x2 hay 3x3
        rubik_type = "2x2" if self.is_2x2 else "3x3"
        
        # Lấy danh sách tất cả các thuật toán để so sánh
        algorithm_registry = self.get_algorithm_registry()
        
        if self.is_2x2:
            # Với Rubik 2x2, bao gồm tất cả các thuật toán
            algorithms_to_compare = [
                0,  # BFS
                1,  # DFS
                2,  # UCS
                3,  # IDS
                4,  # A*
                5,  # IDA*
                6,  # Greedy Best-First
                7,  # Hill Climbing Max
                8,  # Hill Climbing Random
                9,  # Simple Hill Climbing
                10, # Pattern Database A*
                11, # Simulated Annealing
                12, # Genetic Algorithm
                13, # Local Beam Search
                14, # AND-OR Graph Search
                15, # Belief States
                16, # AC-3
                17, # Backtracking 1
                18, # Backtracking 2
                19, # Pattern Database (2x2)
                20  # DeepCubeA (2x2)
            ]
            
            # Thông báo cho người dùng về thời gian chạy cho Rubik 2x2
            reply = QMessageBox.question(
                self, 
                "Xác nhận so sánh",
                "So sánh tất cả các thuật toán trên Rubik 2x2 có thể mất nhiều thời gian. Tiếp tục?",
                QMessageBox.Yes | QMessageBox.No, 
                QMessageBox.No
            )
        else:
            # Với Rubik 3x3, loại bỏ các thuật toán chỉ dành cho 2x2
            algorithms_to_compare = [
                0,  # BFS
                1,  # DFS
                2,  # UCS
                3,  # IDS
                4,  # A*
                5,  # IDA* 
                6,  # Greedy Best-First
                7,  # Hill Climbing Max
                8,  # Hill Climbing Random
                9,  # Simple Hill Climbing
                10, # Pattern Database A*
                11, # Simulated Annealing
                12, # Genetic Algorithm
                13, # Local Beam Search
                14, # AND-OR Graph Search
                15, # Belief States
                16, # AC-3
                17, # Backtracking 1
                18  # Backtracking 2
            ]
            
            # Thông báo cảnh báo mạnh mẽ hơn cho Rubik 3x3
            reply = QMessageBox.warning(
                self, 
                "Cảnh báo - So sánh các thuật toán",
                "So sánh TẤT CẢ các thuật toán trên Rubik 3x3 sẽ MẤT RẤT NHIỀU THỜI GIAN và có thể làm chương trình không phản hồi.\n\n" +
                "Một số thuật toán như DFS có thể không bao giờ tìm ra kết quả trong thời gian hợp lý.\n\n" +
                "Bạn có chắc chắn muốn tiếp tục?",
                QMessageBox.Yes | QMessageBox.No, 
                QMessageBox.No
            )
            
        # Kiểm tra phản hồi người dùng
        if reply == QMessageBox.No:
            return
        
        # Tạo progress dialog với nhiều thông tin hơn
        progress = QProgressDialog("Đang chuẩn bị so sánh các thuật toán...", "Hủy", 0, len(algorithms_to_compare), self)
        progress.setWindowTitle("Đang so sánh thuật toán")
        progress.setWindowModality(Qt.WindowModal)
        progress.setMinimumWidth(400)  # Đặt chiều rộng tối thiểu để nhìn rõ thông tin
        progress.show()
        
        # Lưu kết quả so sánh
        comparison_results = []
        
        # Đếm số thuật toán đã tìm được lời giải
        algorithms_with_solution = 0
        
        # Ánh xạ thuật toán ID với hàm
        algorithm_funcs = {
            "bfs": bfs,
            "dfs": dfs,
            "ucs": ucs,
            "ids": ids,
            "a_star": a_star,
            "ida_star": ida_star,
            "greedy_best_first": greedy_best_first,
            "hill_climbing_max": hill_climbing_max,
            "hill_climbing_random": hill_climbing_random,
            "simple_hill_climbing": simple_hill_climbing,
            "pdb_astar": pdb_astar,
            "deepcube": lambda state, time_limit, return_stats: DeepCubeSolver().solve(state),
            "pdb_2x2": lambda state, time_limit, return_stats: self.wrap_pdb_2x2_solver(state, time_limit),
            "deepcube_2x2": lambda state, time_limit, return_stats: self.wrap_deepcube_2x2_solver(state, time_limit),
            "simulated_annealing": simulated_annealing,
            "genetic_algorithm": genetic_algorithm,
            "local_beam_search": local_beam_search,
            "and_or_search": and_or_graph_search,
            "belief_states": belief_states_search,
            "ac3": ac3_search,
            "backtracking_1": backtracking_search_strategy1,
            "backtracking_2": backtracking_search_strategy2,
        }
        
        # Lấy time limit từ spinbox
        time_limit = self.time_limit_spin.value()
        
        # Đặt thời gian giới hạn cho mỗi thuật toán (mặc định 30 giây nếu không có spinbox)
        if not hasattr(self, 'time_limit_spin'):
            time_limit = 30
        
        # Lặp qua từng thuật toán để thực hiện so sánh
        for i, algo_id in enumerate(algorithms_to_compare):
            # Cập nhật progress dialog
            progress.setValue(i)
            if progress.wasCanceled():
                break
                
            # Lấy tên và hàm thuật toán
            if algo_id not in algorithm_registry:
                continue
                
            algorithm_display_name, algorithm_name = algorithm_registry[algo_id]
            progress.setLabelText(f"Đang chạy thuật toán ({i+1}/{len(algorithms_to_compare)}): {algorithm_display_name}")
            
            # Hiển thị ước tính thời gian còn lại
            if i > 0:
                avg_time_per_algo = (time.time() - start_time) / i
                remaining_time = avg_time_per_algo * (len(algorithms_to_compare) - i)
                progress.setLabelText(f"Đang chạy thuật toán ({i+1}/{len(algorithms_to_compare)}): {algorithm_display_name}\nThời gian còn lại: {remaining_time:.1f} giây")
            
            # Kiểm tra nếu hàm thuật toán tồn tại
            if algorithm_name not in algorithm_funcs:
                comparison_results.append({
                    "Algorithm": algorithm_display_name,
                    "Found Solution": "N/A",
                    "Time (s)": "N/A",
                    "Nodes Visited": "N/A",
                    "Solution Length": "N/A",
                    "Memory Usage": "N/A",
                    "Effective Branching": "N/A",
                    "Time Complexity": "N/A",
                    "Space Complexity": "N/A"
                })
                continue
                
            # Tạo bản sao trạng thái để đảm bảo mỗi thuật toán chạy trên cùng một trạng thái
            state_copy = current_state
            
            try:
                # Chạy thuật toán
                QCoreApplication.processEvents()  # Cập nhật UI để đảm bảo progress dialog hiển thị
                algorithm_func = algorithm_funcs[algorithm_name]
                
                # Bắt đầu đo thời gian
                start_time = time.time()
                
                # Chạy thuật toán với time limit
                result = algorithm_func(state_copy, time_limit=time_limit, return_stats=True)
                
                # Kiểm tra định dạng kết quả
                if len(result) == 4:  # Định dạng mới (path, nodes_visited, time_taken, stats)
                    path, nodes_visited, time_taken, stats = result
                else:  # Định dạng cũ (path, nodes_visited, time_taken)
                    path, nodes_visited, time_taken = result
                    stats = {}  # Dict trống cho các thuật toán cũ
                
                # Thêm kết quả vào danh sách so sánh
                found_solution = "Yes" if path else "No"
                solution_length = len(path) if path else "N/A"
                
                # Lấy thông tin về độ phức tạp thuật toán
                time_complexity = self.get_time_complexity(algorithm_name)
                space_complexity = self.get_space_complexity(algorithm_name)
                
                memory_usage = stats.get('memory_used', "N/A")
                effective_branching = f"{stats.get('effective_branching', 'N/A')}"
                if effective_branching != "N/A":
                    effective_branching = f"{float(effective_branching):.2f}"
                
                result_data = {
                    "Algorithm": algorithm_display_name,
                    "Found Solution": found_solution,
                    "Time (s)": f"{time_taken:.2f}" if found_solution == "Yes" else f"{time_limit}+",
                    "Nodes Visited": nodes_visited,
                    "Solution Length": solution_length,
                    "Memory Usage": memory_usage,
                    "Effective Branching": effective_branching,
                    "Time Complexity": time_complexity,
                    "Space Complexity": space_complexity
                }
                
                comparison_results.append(result_data)
                
                # Cập nhật đếm số thuật toán thành công
                if found_solution == "Yes":
                    algorithms_with_solution += 1
                
            except Exception as e:
                print(f"Lỗi khi chạy thuật toán {algorithm_display_name}: {e}")
                comparison_results.append({
                    "Algorithm": algorithm_display_name,
                    "Found Solution": "Error",
                    "Time (s)": "N/A",
                    "Nodes Visited": "N/A",
                    "Solution Length": "N/A",
                    "Memory Usage": "N/A",
                    "Effective Branching": "N/A",
                    "Time Complexity": time_complexity if 'time_complexity' in locals() else "N/A",
                    "Space Complexity": space_complexity if 'space_complexity' in locals() else "N/A"
                })
        
        # Đóng progress dialog
        progress.setValue(len(algorithms_to_compare))
        
        # Hiển thị thông tin tóm tắt kết quả và một số phân tích
        summary_text = f"<h3>Kết quả so sánh thuật toán:</h3>"
        summary_text += f"<p><b>• Tổng số thuật toán đã thử:</b> {len(algorithms_to_compare)}<br>"
        summary_text += f"<b>• Số thuật toán tìm thấy lời giải:</b> {algorithms_with_solution}<br>"
        summary_text += f"<b>• Số thuật toán không tìm thấy lời giải:</b> {len(algorithms_to_compare) - algorithms_with_solution}</p>"
        
        # Thêm phân tích nhanh cho các thuật toán tìm được lời giải
        if algorithms_with_solution > 0:
            # Lọc ra các thuật toán có lời giải
            solved_algorithms = [r for r in comparison_results if r["Found Solution"] == "Yes"]
            
            # Tìm thuật toán nhanh nhất
            fastest_algo = min(solved_algorithms, key=lambda x: float(x["Time (s)"]) if x["Time (s)"] != "N/A" else float('inf'))
            
            # Tìm thuật toán có độ dài lời giải ngắn nhất
            shortest_path_algo = min(solved_algorithms, 
                                    key=lambda x: int(x["Solution Length"]) if x["Solution Length"] != "N/A" else float('inf'))
            
            # Hiển thị thông tin phân tích
            summary_text += f"<h4>Phân tích thuật toán:</h4>"
            summary_text += f"<p><b>• Thuật toán nhanh nhất:</b> {fastest_algo['Algorithm']} ({fastest_algo['Time (s)']} giây)<br>"
            summary_text += f"<b>• Thuật toán có lời giải ngắn nhất:</b> {shortest_path_algo['Algorithm']} ({shortest_path_algo['Solution Length']} bước)<br></p>"
        
        # Tạo dialog để hiển thị kết quả chi tiết
        results_dialog = QDialog(self)
        results_dialog.setWindowTitle("Kết quả so sánh thuật toán")
        results_dialog.setMinimumWidth(600)
        results_dialog.setMinimumHeight(400)
        
        # Layout cho dialog
        dialog_layout = QVBoxLayout()
        
        # Hiển thị tóm tắt
        summary_label = QLabel(summary_text)
        summary_label.setTextFormat(Qt.RichText)
        dialog_layout.addWidget(summary_label)
        
        # Hiển thị bảng kết quả chi tiết
        results_table = QTableWidget()
        results_table.setRowCount(len(comparison_results))
        results_table.setColumnCount(7)  # Giảm số cột để nhìn rõ hơn
        
        # Đặt tiêu đề cho bảng
        results_table.setHorizontalHeaderLabels([
            "Thuật toán", "Tìm thấy lời giải", "Thời gian (s)", 
            "Số node thăm", "Độ dài lời giải", "Bộ nhớ sử dụng", 
            "Hệ số phân nhánh"
        ])
        
        # Thêm dữ liệu vào bảng
        for row, result in enumerate(comparison_results):
            results_table.setItem(row, 0, QTableWidgetItem(result["Algorithm"]))
            results_table.setItem(row, 1, QTableWidgetItem(result["Found Solution"]))
            results_table.setItem(row, 2, QTableWidgetItem(str(result["Time (s)"])))
            results_table.setItem(row, 3, QTableWidgetItem(str(result["Nodes Visited"])))
            results_table.setItem(row, 4, QTableWidgetItem(str(result["Solution Length"])))
            results_table.setItem(row, 5, QTableWidgetItem(str(result["Memory Usage"])))
            results_table.setItem(row, 6, QTableWidgetItem(str(result["Effective Branching"])))
            
            # Tô màu cho các hàng có tìm thấy lời giải
            if result["Found Solution"] == "Yes":
                for col in range(7):
                    item = results_table.item(row, col)
                    item.setBackground(QColor(200, 255, 200))  # Màu xanh nhạt
        
        # Điều chỉnh kích thước cột
        results_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        results_table.setEditTriggers(QTableWidget.NoEditTriggers)  # Vô hiệu hóa sửa trực tiếp
        
        dialog_layout.addWidget(results_table)
        
        # Các nút điều khiển
        buttons_layout = QHBoxLayout()
        export_btn = QPushButton("Xuất ra Excel")
        export_btn.clicked.connect(lambda: self.export_comparison_results(comparison_results, rubik_type))
        
        close_btn = QPushButton("Đóng")
        close_btn.clicked.connect(results_dialog.accept)
        
        buttons_layout.addWidget(export_btn)
        buttons_layout.addWidget(close_btn)
        dialog_layout.addLayout(buttons_layout)
        
        results_dialog.setLayout(dialog_layout)
        results_dialog.exec_()
    
    def get_time_complexity(self, algorithm_name):
        """Trả về độ phức tạp thời gian của thuật toán"""
        complexities = {
            "bfs": "O(b^d)",
            "dfs": "O(b^m)",
            "ucs": "O(b^{C*/ε})",
            "ids": "O(b^d)",
            "a_star": "O(b^d)",
            "ida_star": "O(b^d)",
            "greedy_best_first": "O(b^m)",
            "hill_climbing_max": "O(b*m)",
            "hill_climbing_random": "O(b*m)",
            "simple_hill_climbing": "O(b*m)",
            "pdb_astar": "O(b^(d*h(n)))",
            "deepcube": "O(1) [inference]",
            "pdb_2x2": "O(1) [lookup]",
            "deepcube_2x2": "O(1) [inference]",
            "simulated_annealing": "O(n)",
            "genetic_algorithm": "O(p*g)",
            "local_beam_search": "O(k*b*m)",
            "and_or_search": "O(b^m)",
            "belief_states": "O(|S|^2)",
            "ac3": "O(n^2*d^3)",
            "backtracking_1": "O(d^n)",
            "backtracking_2": "O(d^n)"
        }
        return complexities.get(algorithm_name, "N/A")
    
    def get_space_complexity(self, algorithm_name):
        """Trả về độ phức tạp không gian của thuật toán"""
        complexities = {
            "bfs": "O(b^d)",
            "dfs": "O(b*m)",
            "ucs": "O(b^{C*/ε})",
            "ids": "O(b*d)",
            "a_star": "O(b^d)",
            "ida_star": "O(b*d)",
            "greedy_best_first": "O(b^m)",
            "hill_climbing_max": "O(b)",
            "hill_climbing_random": "O(b)",
            "simple_hill_climbing": "O(b)",
            "pdb_astar": "O(b^d) + PDB",
            "deepcube": "O(model size)",
            "pdb_2x2": "O(PDB size)",
            "deepcube_2x2": "O(model size)",
            "simulated_annealing": "O(1)",
            "genetic_algorithm": "O(p)",
            "local_beam_search": "O(k)",
            "and_or_search": "O(b^m)",
            "belief_states": "O(|S|)",
            "ac3": "O(n^2*d^2)",
            "backtracking_1": "O(n)",
            "backtracking_2": "O(n)"
        }
        return complexities.get(algorithm_name, "N/A")
    
    def export_comparison_results(self, comparison_results, rubik_type):
        """Xuất kết quả so sánh ra file Excel"""
        if not comparison_results:
            QMessageBox.warning(self, "Không có kết quả", "Không có kết quả so sánh nào để xuất!")
            return
            
        try:
            # Lấy trạng thái hiện tại của Rubik
            current_state = self.get_current_state()
            if current_state is None:
                QMessageBox.warning(self, "Lỗi", "Không thể lấy trạng thái Rubik hiện tại!")
                return
            
            # Tạo tên file với timestamp
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename, _ = QFileDialog.getSaveFileName(
                self, "Lưu kết quả so sánh", f"algorithm_comparison_{rubik_type}_{timestamp}.xlsx", "Excel Files (*.xlsx)"
            )
            
            if not filename:
                return  # Người dùng hủy lưu
                
            # Tạo DataFrame từ kết quả
            df = pd.DataFrame(comparison_results)
            
            # Tạo Excel writer với định dạng
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                # Ghi dữ liệu
                df.to_excel(writer, sheet_name='Kết quả so sánh', index=False)
                
                # Định dạng file
                workbook = writer.book
                worksheet = writer.sheets['Kết quả so sánh']
                
                # Định dạng tiêu đề
                for col_num, col_name in enumerate(df.columns, 1):
                    cell = worksheet.cell(row=1, column=col_num)
                    cell.font = openpyxl.styles.Font(bold=True)
                    cell.alignment = openpyxl.styles.Alignment(horizontal='center')
                    cell.fill = openpyxl.styles.PatternFill(start_color="FFFF00", end_color="FFFF00", fill_type="solid")
                
                # Điều chỉnh độ rộng cột
                for col_num, col_name in enumerate(df.columns, 1):
                    column_width = max(len(str(col_name)) + 2, max(len(str(df.iloc[i][col_name])) for i in range(len(df))) + 2)
                    worksheet.column_dimensions[openpyxl.utils.get_column_letter(col_num)].width = min(column_width, 30)
                
                # Điều chỉnh fontSize cột đầu tiên (Algorithm)
                for row_num in range(2, len(df) + 2):
                    cell = worksheet.cell(row=row_num, column=1)
                    cell.font = openpyxl.styles.Font(bold=True)
                    
                    # Tô màu các hàng có lời giải thành công
                    if df.iloc[row_num-2]["Found Solution"] == "Yes":
                        for col_num in range(1, len(df.columns) + 1):
                            cell = worksheet.cell(row=row_num, column=col_num)
                            cell.fill = openpyxl.styles.PatternFill(
                                start_color="E2EFDA", 
                                end_color="E2EFDA", 
                                fill_type="solid"
                            )
                    
                    # Tô màu các hàng có lỗi
                    if df.iloc[row_num-2]["Found Solution"] == "Error":
                        for col_num in range(1, len(df.columns) + 1):
                            cell = worksheet.cell(row=row_num, column=col_num)
                            cell.fill = openpyxl.styles.PatternFill(
                                start_color="FFCCCC", 
                                end_color="FFCCCC", 
                                fill_type="solid"
                            )
                
                # Thêm sheet thông tin về trạng thái Rubik
                if self.is_2x2:
                    state_info = {
                        "Property": ["Rubik Type", "Corner Permutation (CP)", "Corner Orientation (CO)"],
                        "Value": [
                            "2x2",
                            str(current_state.cp),
                            str(current_state.co)
                        ]
                    }
                else:
                    state_info = {
                        "Property": ["Rubik Type", "Corner Permutation (CP)", "Corner Orientation (CO)", 
                                    "Edge Permutation (EP)", "Edge Orientation (EO)"],
                        "Value": [
                            "3x3",
                            str(current_state.cp),
                            str(current_state.co),
                            str(current_state.ep),
                            str(current_state.eo)
                        ]
                    }
                state_df = pd.DataFrame(state_info)
                state_df.to_excel(writer, sheet_name='Trạng thái Rubik', index=False)
                
                # Định dạng sheet trạng thái
                ws_state = writer.sheets['Trạng thái Rubik']
                ws_state.column_dimensions['A'].width = 25
                ws_state.column_dimensions['B'].width = 50
                
                # Thêm sheet giải thích
                explanation = {
                    "Term": [
                        "Time Complexity", 
                        "Space Complexity", 
                        "b", 
                        "d", 
                        "m", 
                        "n",
                        "p",
                        "g",
                        "k",
                        "PDB",
                        "|S|"
                    ],
                    "Description": [
                        "Tăng trưởng thời gian thực thi theo kích thước đầu vào",
                        "Tăng trưởng bộ nhớ cần thiết theo kích thước đầu vào",
                        "Hệ số phân nhánh (số nước đi có thể từ mỗi trạng thái)",
                        "Độ sâu của lời giải tối ưu",
                        "Độ sâu tối đa của không gian tìm kiếm",
                        "Số biến số (trong Rubik là số viên)",
                        "Kích thước quần thể trong thuật toán di truyền",
                        "Số thế hệ trong thuật toán di truyền",
                        "Số beam trong local beam search",
                        "Pattern Database - CSDL mẫu đã tính sẵn",
                        "Kích thước không gian trạng thái"
                    ]
                }
                explanation_df = pd.DataFrame(explanation)
                explanation_df.to_excel(writer, sheet_name='Giải thích', index=False)
                
                # Thêm sheet phân tích dữ liệu và biểu đồ
                # Tạo dataframe chỉ chứa thuật toán thành công
                successful_df = df[df["Found Solution"] == "Yes"].copy()
                
                if not successful_df.empty:
                    # Chuyển cột thời gian và số node thành số
                    successful_df["Time (s)"] = successful_df["Time (s)"].astype(float)
                    
                    # Sắp xếp theo thời gian tăng dần
                    successful_df = successful_df.sort_values("Time (s)")
                    
                    # Tạo dataframe cho biểu đồ
                    chart_data = {
                        "Algorithm": successful_df["Algorithm"].tolist(),
                        "Time (s)": successful_df["Time (s)"].tolist(),
                        "Solution Length": successful_df["Solution Length"].astype(str).astype(float).tolist()
                    }
                    chart_df = pd.DataFrame(chart_data)
                    
                    # Ghi ra sheet phân tích
                    chart_df.to_excel(writer, sheet_name='Phân tích', index=False)
                    
                    # Tạo thêm bảng xếp hạng
                    ranking_data = {
                        "Tiêu chí": [
                            "Thuật toán nhanh nhất",
                            "Thuật toán có lời giải ngắn nhất",
                            "Thuật toán sử dụng ít node nhất",
                            "Thuật toán có hệ số phân nhánh thấp nhất"
                        ],
                        "Thuật toán": [
                            successful_df.iloc[0]["Algorithm"],
                            successful_df.sort_values("Solution Length").iloc[0]["Algorithm"],
                            successful_df.sort_values("Nodes Visited").iloc[0]["Algorithm"],
                            "N/A"  # Mặc định
                        ],
                        "Giá trị": [
                            f"{successful_df.iloc[0]['Time (s)']} giây",
                            f"{successful_df.sort_values('Solution Length').iloc[0]['Solution Length']} bước",
                            f"{successful_df.sort_values('Nodes Visited').iloc[0]['Nodes Visited']} nodes",
                            "N/A"  # Mặc định
                        ]
                    }
                    
                    # Định dạng sheet phân tích
                    ws_analysis = writer.sheets['Phân tích']
                    
                    # Thêm bảng xếp hạng vào sheet phân tích
                    ranking_df = pd.DataFrame(ranking_data)
                    ranking_df.to_excel(writer, sheet_name='Xếp hạng', index=False)
                    
                    # Định dạng sheet xếp hạng
                    ws_ranking = writer.sheets['Xếp hạng']
                    ws_ranking.column_dimensions['A'].width = 30
                    ws_ranking.column_dimensions['B'].width = 30
                    ws_ranking.column_dimensions['C'].width = 20
                    
                    # Tô màu cho header
                    for col_num in range(1, 4):
                        cell = ws_ranking.cell(row=1, column=col_num)
                        cell.font = openpyxl.styles.Font(bold=True)
                        cell.fill = openpyxl.styles.PatternFill(
                            start_color="4472C4", 
                            end_color="4472C4", 
                            fill_type="solid"
                        )
                        cell.font = openpyxl.styles.Font(bold=True, color="FFFFFF")
                
                # Định dạng sheet giải thích
                ws_explain = writer.sheets['Giải thích']
                ws_explain.column_dimensions['A'].width = 20
                ws_explain.column_dimensions['B'].width = 70
            
            QMessageBox.information(self, "Xuất thành công", f"Kết quả so sánh đã được xuất ra file {filename}")
            
        except Exception as e:
            QMessageBox.critical(self, "Lỗi khi xuất", f"Đã xảy ra lỗi: {str(e)}")
            print(f"Lỗi khi export: {e}")


