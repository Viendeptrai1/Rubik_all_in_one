from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from rubik import RubikCube

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

        # Create tab widget for algorithm groups
        tabs = QTabWidget()
        
        # Define algorithm groups - SIMPLIFIED
        algorithm_groups = {
            "Search": [
                "Breadth-First Search", "A* Search"
            ]
        }
        
        # Create tabs for each algorithm group
        for group_name, algorithms in algorithm_groups.items():
            algo_group = AlgorithmGroup(group_name, algorithms)
            algo_group.buttonClicked.connect(self.on_algorithm_clicked)
            tabs.addTab(algo_group, group_name)
        
        main_layout.addWidget(tabs)
        
        # Add description area
        description_group = QGroupBox("Algorithm Description")
        description_layout = QVBoxLayout()
        self.description_text = QTextEdit()
        self.description_text.setReadOnly(True)
        description_layout.addWidget(self.description_text)
        description_group.setLayout(description_layout)
        main_layout.addWidget(description_group)
        
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
        self.rubik_widget.rubik = RubikCube()
        self.description_text.clear()
    
    def shuffle_cube(self):
        """Xáo trộn khối Rubik ngẫu nhiên"""
        self.rubik_widget.rubik.scramble(20)
    
    def on_algorithm_clicked(self, algo_name):
        """Hiển thị mô tả thuật toán khi được chọn"""
        descriptions = {
            "Breadth-First Search": """Breadth-First Search khám phá tất cả các nước đi ở độ sâu hiện tại
            trước khi chuyển sang mức độ sâu tiếp theo. Đảm bảo giải pháp tối ưu nhưng
            tiêu tốn lượng bộ nhớ lớn.""",
            
            "A* Search": """Thuật toán A* sử dụng hàm heuristic để tìm đường
            đi hứa hẹn nhất. Đảm bảo giải pháp tối ưu nếu heuristic là admissible."""
        }
        
        if algo_name in descriptions:
            self.description_text.setText(descriptions[algo_name])
        else:
            self.description_text.setText("")
