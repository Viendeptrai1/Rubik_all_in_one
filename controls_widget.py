from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from rubik_3x3 import RubikCube
from rubik_2x2 import RubikCube2x2
from RubikState.rubik_chen import RubikState, SOLVED_STATE as SOLVED_STATE_3X3
from RubikState.rubik_2x2 import Rubik2x2State, SOLVED_STATE as SOLVED_STATE_2X2
import time

class ControlsWidget(QWidget):
    def __init__(self, rubik_widget):
        super().__init__()
        self.rubik_widget = rubik_widget
        self.init_ui()

    def set_rubik_widget(self, rubik_widget):
        """Cập nhật widget rubik hiện tại khi chuyển tab"""
        self.rubik_widget = rubik_widget
        # Cập nhật trạng thái nút theo widget mới
        self.update_buttons()
        # Cập nhật hiển thị trạng thái
        self.update_state_display()

    def update_buttons(self):
        """Cập nhật trạng thái nút dựa trên widget hiện tại"""
        # Không làm gì trong trường hợp này vì chúng ta không có nút solve_btn
        pass
        
    def update_state_display(self):
        """Cập nhật hiển thị trạng thái Rubik"""
        state = self.rubik_widget.rubik.get_state()
        
        if isinstance(self.rubik_widget.rubik, RubikCube2x2):
            # Hiển thị đơn giản cho Rubik 2x2
            self.state_display.setText("Trạng thái Rubik 2x2")
        else:
            # Hiển thị đơn giản cho Rubik 3x3
            self.state_display.setText("Trạng thái Rubik 3x3")

    def init_ui(self):
        # Main layout
        main_layout = QVBoxLayout()
        
        # Input moves group
        moves_group = QGroupBox("Input Moves")
        moves_layout = QVBoxLayout()
        self.moves_input = QLineEdit()
        self.moves_input.setPlaceholderText("Enter moves (e.g. R U R' U')")
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
        
        # Hiển thị trạng thái
        state_group = QGroupBox("Trạng thái Rubik")
        state_layout = QVBoxLayout()
        self.state_display = QTextEdit()
        self.state_display.setReadOnly(True)
        state_layout.addWidget(self.state_display)
        state_group.setLayout(state_layout)
        main_layout.addWidget(state_group)
        
        # Cập nhật hiển thị trạng thái ban đầu
        self.update_state_display()
        
        main_layout.addStretch()
        self.setLayout(main_layout)
    
    def apply_moves(self):
        """Áp dụng các bước di chuyển từ input"""
        moves_str = self.moves_input.text()
        if not moves_str:
            return
            
        moves = self.parse_moves(moves_str)
        for face, clockwise in moves:
            self.rubik_widget.rubik.rotate_face(face, clockwise)
            
        # Cập nhật hiển thị trạng thái sau khi thực hiện các nước đi
        self.update_state_display()
    
    def parse_moves(self, moves_str):
        """Chuyển đổi chuỗi moves thành list (face, clockwise)"""
        moves = []
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
        if isinstance(self.rubik_widget.rubik, RubikCube2x2):
            self.rubik_widget.rubik = RubikCube2x2()
        else:
            self.rubik_widget.rubik = RubikCube()
        
        # Cập nhật hiển thị trạng thái
        self.update_state_display()
    
    def shuffle_cube(self):
        """Xáo trộn khối Rubik ngẫu nhiên"""
        self.rubik_widget.rubik.scramble(20)
        
        # Cập nhật hiển thị trạng thái sau khi xáo trộn
        self.update_state_display()
