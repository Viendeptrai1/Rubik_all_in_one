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
        # Main layout
        main_layout = QVBoxLayout()
        
        # Input moves group
        moves_group = QGroupBox("Input Moves")
        moves_layout = QVBoxLayout()
        self.moves_input = QLineEdit()
        self.moves_input.setPlaceholderText("Enter moves (e.g. R U R' U')")
        # Kết nối sự kiện Enter với hàm apply_moves
        self.moves_input.returnPressed.connect(self.apply_moves)
        
        apply_btn = QPushButton("Apply Moves")
        apply_btn.clicked.connect(self.apply_moves)
        moves_layout.addWidget(self.moves_input)
        moves_layout.addWidget(apply_btn)
        moves_group.setLayout(moves_layout)
        main_layout.addWidget(moves_group)

        # Control buttons
        buttons_layout = QHBoxLayout()
        reset_btn = QPushButton("Reset")
        shuffle_btn = QPushButton("Shuffle")
        reset_btn.clicked.connect(self.reset_cube)
        shuffle_btn.clicked.connect(self.shuffle_cube)
        buttons_layout.addWidget(reset_btn)
        buttons_layout.addWidget(shuffle_btn)
        main_layout.addLayout(buttons_layout)
        
        # Solver Algorithm group
        solver_group = QGroupBox("Thuật toán giải")
        solver_layout = QVBoxLayout()
        
        # Combobox để chọn thuật toán
        self.algorithm_combo = QComboBox()
        self.algorithm_combo.addItem("BFS (Breadth-First Search)")
        self.algorithm_combo.addItem("A* (A-star)")
        solver_layout.addWidget(QLabel("Chọn thuật toán:"))
        solver_layout.addWidget(self.algorithm_combo)
        
        # Thêm các option cho A*
        astar_options_layout = QHBoxLayout()
        astar_options_layout.addWidget(QLabel("Giới hạn thời gian (giây):"))
        self.time_limit_spin = QSpinBox()
        self.time_limit_spin.setRange(1, 300)
        self.time_limit_spin.setValue(30)
        astar_options_layout.addWidget(self.time_limit_spin)
        solver_layout.addLayout(astar_options_layout)
        
        # Nút giải Rubik
        solve_btn = QPushButton("Giải Rubik")
        solve_btn.clicked.connect(self.solve_rubik)
        solver_layout.addWidget(solve_btn)
        
        solver_group.setLayout(solver_layout)
        main_layout.addWidget(solver_group)
        
        # Solution Results group
        solution_group = QGroupBox("Kết quả giải")
        solution_layout = QVBoxLayout()
        
        # Hiển thị trạng thái giải
        self.solution_status = QLabel("Sẵn sàng")
        solution_layout.addWidget(self.solution_status)
        
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
        solution_layout.addLayout(stats_layout)
        
        # Hiển thị lời giải
        solution_layout.addWidget(QLabel("Lời giải:"))
        self.solution_moves = QTextEdit()
        self.solution_moves.setReadOnly(True)
        self.solution_moves.setFixedHeight(80)
        solution_layout.addWidget(self.solution_moves)
        
        # Nút áp dụng lời giải
        apply_solution_btn = QPushButton("Áp dụng lời giải")
        apply_solution_btn.clicked.connect(self.apply_solution)
        solution_layout.addWidget(apply_solution_btn)
        
        solution_group.setLayout(solution_layout)
        main_layout.addWidget(solution_group)
        
        # State Display panel
        state_group = QGroupBox("Rubik State")
        state_layout = QVBoxLayout()
        
        # TextEdit để hiển thị trạng thái
        self.state_display = QTextEdit()
        self.state_display.setReadOnly(True)
        self.state_display.setFixedHeight(200)  # Chiều cao cố định
        state_layout.addWidget(self.state_display)
        
        state_group.setLayout(state_layout)
        main_layout.addWidget(state_group)
        
        main_layout.addStretch()
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
        
        # Lấy thuật toán đã chọn
        algorithm_index = self.algorithm_combo.currentIndex()
        time_limit = self.time_limit_spin.value()
        
        # Hiển thị thông tin về trạng thái giải
        cube_type = "Rubik 2x2" if self.is_2x2 else "Rubik 3x3"
        algorithm_type = "BFS" if algorithm_index == 0 else "A*"
        self.solution_status.setText(f"Đang giải {cube_type} bằng {algorithm_type}...")
        
        # Chạy thuật toán giải
        try:
            from RubikState.rubik_solver import bfs, a_star
            
            start_time = time.time()
            path, nodes_visited, time_taken = bfs(current_state) if algorithm_index == 0 else a_star(current_state)
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
    
    def apply_solution(self):
        # Gỡ lỗi
        print("Áp dụng lời giải:", self.current_solution)
        
        if not self.current_solution:
            self.solution_status.setText("Chưa có lời giải để áp dụng!")
            return
            
        # Áp dụng lời giải cho Rubik 3D
        self.apply_moves_to_3d_cube(self.current_solution)
