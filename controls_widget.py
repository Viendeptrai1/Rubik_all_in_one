from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from rubik_3x3 import RubikCube
from rubik_2x2 import RubikCube2x2
import time
import random
from RubikState.rubik_solver import a_star, bfs

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
        # Main layout - Sử dụng QVBoxLayout cho toàn bộ widget
        main_layout = QVBoxLayout()
        
        # ===== PHẦN TRÊN: ĐIỀU KHIỂN VÀ THÔNG TIN (chiếm 1/2 diện tích) =====
        top_widget = QWidget()
        top_layout = QHBoxLayout()
        top_widget.setLayout(top_layout)
        
        # -- PHẦN 1: ĐIỀU KHIỂN CƠ BẢN (bên trái) --
        basic_controls = QGroupBox("Điều khiển cơ bản")
        basic_layout = QVBoxLayout()
        
        # Input moves group
        moves_input = QLineEdit()
        moves_input.setPlaceholderText("Nhập nước đi (ví dụ: R U R' U')")
        self.moves_input = moves_input
        # Kết nối sự kiện Enter với hàm apply_moves
        self.moves_input.returnPressed.connect(self.apply_moves)
        
        apply_btn = QPushButton("Áp dụng")
        apply_btn.clicked.connect(self.apply_moves)
        
        basic_layout.addWidget(QLabel("Nhập nước đi:"))
        basic_layout.addWidget(moves_input)
        basic_layout.addWidget(apply_btn)
        
        # Control buttons
        buttons_layout = QHBoxLayout()
        reset_btn = QPushButton("Reset")
        shuffle_btn = QPushButton("Xáo trộn")
        reset_btn.clicked.connect(self.reset_cube)
        shuffle_btn.clicked.connect(self.shuffle_cube)
        buttons_layout.addWidget(reset_btn)
        buttons_layout.addWidget(shuffle_btn)
        basic_layout.addLayout(buttons_layout)
        
        # Solution Results
        basic_layout.addWidget(QLabel("Kết quả giải:"))
        
        # Hiển thị trạng thái giải
        self.solution_status = QLabel("Sẵn sàng")
        basic_layout.addWidget(self.solution_status)
        
        # Hiển thị thống kê
        stats_layout = QGridLayout()
        stats_layout.addWidget(QLabel("Thời gian:"), 0, 0)
        self.solution_time = QLabel("0 giây")
        stats_layout.addWidget(self.solution_time, 0, 1)
        
        stats_layout.addWidget(QLabel("Số nút đã duyệt:"), 1, 0)
        self.nodes_visited = QLabel("0")
        stats_layout.addWidget(self.nodes_visited, 1, 1)
        
        stats_layout.addWidget(QLabel("Độ dài lời giải:"), 2, 0)
        self.solution_length = QLabel("0")
        stats_layout.addWidget(self.solution_length, 2, 1)
        basic_layout.addLayout(stats_layout)
        
        # Hiển thị lời giải
        basic_layout.addWidget(QLabel("Lời giải:"))
        self.solution_moves = QTextEdit()
        self.solution_moves.setReadOnly(True)
        self.solution_moves.setFixedHeight(60)
        basic_layout.addWidget(self.solution_moves)
        
        # Nút áp dụng lời giải
        apply_solution_btn = QPushButton("Áp dụng lời giải")
        apply_solution_btn.clicked.connect(self.apply_solution)
        basic_layout.addWidget(apply_solution_btn)
        
        basic_controls.setLayout(basic_layout)
        
        # -- PHẦN 2: THÔNG TIN RUBIK (bên phải) --
        info_panel = QGroupBox("Thông tin rubik")
        info_layout = QVBoxLayout()
        
        # TextEdit để hiển thị trạng thái
        self.state_display = QTextEdit()
        self.state_display.setReadOnly(True)
        info_layout.addWidget(self.state_display)
        
        info_panel.setLayout(info_layout)
        
        # Thêm hai phần vào top_layout
        top_layout.addWidget(basic_controls, 1)  # Tỷ lệ 1
        top_layout.addWidget(info_panel, 1)      # Tỷ lệ 1
        
        # ===== PHẦN DƯỚI: CÁC NHÓM THUẬT TOÁN (chiếm 1/2 diện tích) =====
        algo_widget = QWidget()
        algo_layout = QVBoxLayout()
        algo_widget.setLayout(algo_layout)
        
        # Tiêu đề
        algo_layout.addWidget(QLabel("<b>Các nhóm thuật toán</b>"))
        
        # Grid layout cho các nhóm thuật toán (3 cột)
        algo_grid = QGridLayout()
        
        # Tạo button group để chỉ một radio được chọn
        self.algorithm_button_group = QButtonGroup(self)
        
        # Nhóm 1: Tìm kiếm không có thông tin (Uninformed Search)
        uninformed_group = QGroupBox("Tìm kiếm không có thông tin\n(Uninformed Search)")
        uninformed_layout = QVBoxLayout()
        
        # Tạo các radio buttons cho nhóm 1
        self.bfs_radio = QRadioButton("Breadth-First Search")
        self.dfs_radio = QRadioButton("Depth-First Search")
        self.ids_radio = QRadioButton("Iterative Deepening Search")
        self.ucs_radio = QRadioButton("Uniform Cost Search")
        
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
        uninformed_group.setLayout(uninformed_layout)
        
        # Nhóm 2: Tìm kiếm có thông tin (Informed Search)
        informed_group = QGroupBox("Tìm kiếm có thông tin\n(Informed Search)")
        informed_layout = QVBoxLayout()
        
        # Tạo các radio buttons cho nhóm 2
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
        informed_group.setLayout(informed_layout)
        
        # Nhóm 3: Tìm kiếm cục bộ (Local Search)
        local_group = QGroupBox("Tìm kiếm cục bộ\n(Local Search)")
        local_layout = QVBoxLayout()
        
        # Tạo các radio buttons cho nhóm 3
        self.hill_climbing_max_radio = QRadioButton("Hill Climbing Max")
        self.hill_climbing_random_radio = QRadioButton("Hill Climbing Random")
        
        # Thêm vào button group
        self.algorithm_button_group.addButton(self.hill_climbing_max_radio, 7)
        self.algorithm_button_group.addButton(self.hill_climbing_random_radio, 8)
        
        # Thêm vào layout
        local_layout.addWidget(self.hill_climbing_max_radio)
        local_layout.addWidget(self.hill_climbing_random_radio)
        local_group.setLayout(local_layout)
        
        # Thêm các nhóm vào grid layout (1 hàng, 3 cột)
        algo_grid.addWidget(uninformed_group, 0, 0)
        algo_grid.addWidget(informed_group, 0, 1)
        algo_grid.addWidget(local_group, 0, 2)
        
        # Để tiện cho việc thêm các nhóm mới, còn để trống hàng thứ 2
        # algo_grid.addWidget(new_group1, 1, 0)
        # algo_grid.addWidget(new_group2, 1, 1)
        # algo_grid.addWidget(new_group3, 1, 2)
        
        algo_layout.addLayout(algo_grid)
        
        # Thêm options cho các thuật toán
        options_layout = QHBoxLayout()
        options_layout.addWidget(QLabel("Giới hạn thời gian (giây):"))
        self.time_limit_spin = QSpinBox()
        self.time_limit_spin.setRange(1, 300)
        self.time_limit_spin.setValue(30)
        options_layout.addWidget(self.time_limit_spin)
        options_layout.addStretch()
        
        # Nút giải Rubik
        solve_btn = QPushButton("Giải Rubik")
        solve_btn.clicked.connect(self.solve_rubik)
        options_layout.addWidget(solve_btn)
        
        algo_layout.addLayout(options_layout)
        
        # Thêm các phần chính vào main_layout với tỷ lệ 1:1
        splitter = QSplitter(Qt.Vertical)
        splitter.addWidget(top_widget)
        splitter.addWidget(algo_widget)
        
        # Cài đặt tỷ lệ ban đầu 1:1 (50:50)
        splitter.setSizes([500, 500])
        
        # Thêm splitter vào layout chính
        main_layout.addWidget(splitter)
        
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
                    
                    # Kiểm tra ký tự tiếp theo có phải là dấu ' không
                    if i + 1 < len(moves_str) and moves_str[i + 1] == "'":
                        clockwise = False
                        i += 1  # Bỏ qua ký tự '
                    
                    moves.append((face, clockwise))
                i += 1
        else:
            # Xử lý theo khoảng trắng như cũ
            tokens = moves_str.split()
            
            for token in tokens:
                if not token:
                    continue
                    
                face = token[0].upper()
                clockwise = True
                
                if len(token) > 1:
                    if token[1] == "'":
                        clockwise = False
                        
                if face in 'FLUDRB':
                    moves.append((face, clockwise))
                    
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
        self.solution_status.setText("Sẵn sàng")
        self.solution_time.setText("0 giây")
        self.nodes_visited.setText("0")
        self.solution_length.setText("0")
        self.solution_moves.clear()
        self.current_solution = []
        
        # Cập nhật hiển thị trạng thái
        self.update_state_display()
    
    def shuffle_cube(self):
        """Xáo trộn khối Rubik ngẫu nhiên"""
        # Tạo danh sách các nước đi ngẫu nhiên
        faces = ['F', 'B', 'L', 'R', 'U', 'D']
        random_moves = []
        
        last_face = None
        for _ in range(20):
            # Tránh lặp lại mặt vừa xoay
            available_faces = [f for f in faces if f != last_face]
            face = random.choice(available_faces)
            last_face = face
            
            clockwise = random.choice([True, False])
            random_moves.append((face, clockwise))
        
        # Reset khối Rubik
        self.reset_cube()
        
        # Xáo trộn biểu diễn dạng hình (Rubik 3D)
        self.apply_moves_to_3d_cube(random_moves)
        
        # Sau khi xáo trộn, hiển thị trạng thái mới
        # Do animation, việc cập nhật hiển thị sẽ được thực hiện trong hàm update_animation
    
    def solve_rubik(self):
        """Giải Rubik bằng thuật toán đã chọn"""
        # Cập nhật UI
        self.solution_status.setText("Đang giải...")
        self.solution_time.setText("0 giây")
        self.nodes_visited.setText("0")
        self.solution_length.setText("0")
        self.solution_moves.clear()
        self.current_solution = []
        
        # Kiểm tra điều kiện khả thi
        if self.rubik_widget.rubik.animating or self.rubik_widget.move_queue:
            self.solution_status.setText("Không thể giải khi đang thực hiện animation")
            return
        
        # Lấy trạng thái hiện tại
        from RubikState.rubik_chen import RubikState, SOLVED_STATE_3x3, MOVES_3x3
        from RubikState.rubik_2x2 import Rubik2x2State, SOLVED_STATE_2x2, MOVES_2x2
        
        # Tạo trạng thái từ state_tuple
        if self.is_2x2:
            cp, co = self.rubik_widget.rubik.state_tuple
            current_state = Rubik2x2State(cp, co)
            moves_dict = MOVES_2x2
            solved_state = SOLVED_STATE_2x2
        else:
            cp, co, ep, eo = self.rubik_widget.rubik.state_tuple
            current_state = RubikState(cp, co, ep, eo)
            moves_dict = MOVES_3x3
            solved_state = SOLVED_STATE_3x3
        
        # Xác định thuật toán đã chọn
        algorithm_id = self.algorithm_button_group.checkedId()
        
        # Ánh xạ ID với các thuật toán
        algorithm_map = {
            0: ("BFS", "bfs"),
            1: ("DFS", "dfs"),
            2: ("UCS", "ucs"),
            3: ("IDS", "ids"),
            4: ("A*", "a_star"),
            5: ("IDA*", "ida_star"),
            6: ("Greedy Best-First", "greedy_best_first"),
            7: ("Hill Climbing Max", "hill_climbing_max"),
            8: ("Hill Climbing Random", "hill_climbing_random")
        }
        
        if algorithm_id not in algorithm_map:
            self.solution_status.setText("Lỗi: Không tìm thấy thuật toán đã chọn!")
            return
        
        algorithm_name, algorithm_func_name = algorithm_map[algorithm_id]
        
        # Hiển thị thông tin về trạng thái giải
        cube_type = "Rubik 2x2" if self.is_2x2 else "Rubik 3x3"
        self.solution_status.setText(f"Đang giải {cube_type} bằng {algorithm_name}...")
        
        # Chạy thuật toán giải
        time_limit = self.time_limit_spin.value()
        try:
            # Import các thuật toán từ module
            from RubikState.rubik_solver import (
                bfs, dfs, ucs, ids, a_star, ida_star,
                greedy_best_first, hill_climbing_max, hill_climbing_random
            )
            
            # Ánh xạ tên thuật toán với hàm tương ứng
            algorithm_funcs = {
                "bfs": bfs,
                "dfs": dfs,
                "ucs": ucs,
                "ids": ids,
                "a_star": a_star,
                "ida_star": ida_star,
                "greedy_best_first": greedy_best_first,
                "hill_climbing_max": hill_climbing_max,
                "hill_climbing_random": hill_climbing_random
            }
            
            # Lấy hàm thuật toán dựa trên tên
            algorithm_func = algorithm_funcs.get(algorithm_func_name)
            if not algorithm_func:
                self.solution_status.setText(f"Lỗi: Thuật toán {algorithm_func_name} chưa được triển khai!")
                return
            
            start_time = time.time()
            path, nodes_visited, time_taken = algorithm_func(current_state)
            end_time = time.time()
            
            # Xử lý timeout
            if end_time - start_time >= time_limit:
                self.solution_status.setText(f"Đã vượt quá giới hạn thời gian {time_limit}s")
                self.solution_time.setText(f"{end_time - start_time:.2f} giây")
                self.nodes_visited.setText(f"{nodes_visited}")
                return
            
            # Xử lý kết quả
            if path:
                # Đảo ngược thứ tự các nước đi để khớp với quy ước của giao diện
                path = path[::-1]
                
                # Cập nhật UI
                self.solution_status.setText("Đã tìm thấy lời giải!")
                self.solution_time.setText(f"{time_taken:.2f} giây")
                self.nodes_visited.setText(f"{nodes_visited}")
                self.solution_length.setText(f"{len(path)}")
                
                # Hiển thị lời giải
                moves_str = " ".join([move if move.find("'") > 0 else f"{move} " for move in path])
                self.solution_moves.setPlainText(moves_str)
                
                # Lưu lời giải để áp dụng sau
                self.current_solution = self.parse_moves(moves_str)
            else:
                self.solution_status.setText("Không tìm thấy lời giải trong giới hạn thời gian!")
                self.solution_time.setText(f"{time_taken:.2f} giây")
                self.nodes_visited.setText(f"{nodes_visited}")
        except Exception as e:
            self.solution_status.setText(f"Lỗi: {str(e)}")
            print(f"Lỗi khi giải Rubik: {e}")
    
    def apply_solution(self):
        # Gỡ lỗi
        print("Áp dụng lời giải:", self.current_solution)
        
        if not self.current_solution:
            self.solution_status.setText("Chưa có lời giải để áp dụng!")
            return
            
        # Áp dụng lời giải cho Rubik 3D
        self.apply_moves_to_3d_cube(self.current_solution)
