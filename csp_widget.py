import random
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, 
                            QPushButton, QLabel, QRadioButton, QButtonGroup,
                            QGroupBox, QTextEdit, QComboBox, QSplitter, QDialog, QDialogButtonBox,
                            QSpinBox, QFormLayout, QTableWidget, QTableWidgetItem, QHeaderView)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor
from RubikState.rubik_chen import RubikState, SOLVED_STATE_3x3, MOVES_3x3

class CSPWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
    def setup_ui(self):
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        
        # Title
        title_label = QLabel("Rubik CSP (Constraint Satisfaction Problem)")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # Problem statement
        problem_text = QTextEdit()
        problem_text.setReadOnly(True)
        problem_text.setMaximumHeight(120)
        problem_text.setHtml("""
        <div style='font-size: 12px; text-align: justify; margin: 5px;'>
            <p><b>Phát biểu bài toán:</b> Giải bài toán CSP cho Rubik bằng cách tìm các giá trị thỏa mãn ràng buộc.</p>
            <p><b>Biến:</b> Các vị trí góc (cp), định hướng góc (co), vị trí cạnh (ep), định hướng cạnh (eo)</p>
            <p><b>Ràng buộc:</b> 
                (1) Hoán vị góc và cạnh phải hợp lệ; 
                (2) Tổng định hướng góc phải chia hết cho 3; 
                (3) Tổng định hướng cạnh phải chia hết cho 2; 
                (4) Corner parity và edge parity phải khớp nhau
            </p>
            <p><b>Mục tiêu:</b> Từ các giá trị ban đầu đã cho, sử dụng AC-3 để thu hẹp miền giá trị, sau đó dùng backtracking để tìm cấu hình hợp lệ.</p>
        </div>
        """)
        main_layout.addWidget(problem_text)
        
        # Main content splitter
        content_splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(content_splitter)
        
        # Left section - Configuration Input
        left_widget = QWidget()
        left_layout = QVBoxLayout()
        left_widget.setLayout(left_layout)
        
        # Rubik configuration input
        config_group = QGroupBox("Cấu hình ban đầu Rubik")
        config_layout = QVBoxLayout()
        
        # Input options
        input_options_layout = QHBoxLayout()
        
        # Empty configuration button
        self.empty_btn = QPushButton("Cấu hình trống")
        self.empty_btn.clicked.connect(self.generate_empty_config)
        input_options_layout.addWidget(self.empty_btn)
        
        # Partial random button
        self.partial_random_btn = QPushButton("Cấu hình ngẫu nhiên một phần")
        self.partial_random_btn.clicked.connect(self.generate_partial_random)
        input_options_layout.addWidget(self.partial_random_btn)
        
        # Solved configuration button
        self.solved_btn = QPushButton("Cấu hình đã giải")
        self.solved_btn.clicked.connect(self.generate_solved_state)
        input_options_layout.addWidget(self.solved_btn)
        
        config_layout.addLayout(input_options_layout)
        
        # Configuration tables
        tables_layout = QGridLayout()
        
        # Corner Permutation (cp) table
        cp_group = QGroupBox("Corner Permutation (cp)")
        cp_layout = QVBoxLayout()
        self.cp_table = QTableWidget(2, 4)
        self.cp_table.setHorizontalHeaderLabels([f"Góc {i}" for i in range(4)])
        self.cp_table.setVerticalHeaderLabels([f"Hàng {i+1}" for i in range(2)])
        cp_layout.addWidget(self.cp_table)
        cp_group.setLayout(cp_layout)
        tables_layout.addWidget(cp_group, 0, 0)
        
        # Corner Orientation (co) table
        co_group = QGroupBox("Corner Orientation (co)")
        co_layout = QVBoxLayout()
        self.co_table = QTableWidget(2, 4)
        self.co_table.setHorizontalHeaderLabels([f"Góc {i}" for i in range(4)])
        self.co_table.setVerticalHeaderLabels([f"Hàng {i+1}" for i in range(2)])
        co_layout.addWidget(self.co_table)
        co_group.setLayout(co_layout)
        tables_layout.addWidget(co_group, 0, 1)
        
        # Edge Permutation (ep) table
        ep_group = QGroupBox("Edge Permutation (ep)")
        ep_layout = QVBoxLayout()
        self.ep_table = QTableWidget(2, 6)
        self.ep_table.setHorizontalHeaderLabels([f"Cạnh {i}" for i in range(6)])
        self.ep_table.setVerticalHeaderLabels([f"Hàng {i+1}" for i in range(2)])
        ep_layout.addWidget(self.ep_table)
        ep_group.setLayout(ep_layout)
        tables_layout.addWidget(ep_group, 1, 0)
        
        # Edge Orientation (eo) table
        eo_group = QGroupBox("Edge Orientation (eo)")
        eo_layout = QVBoxLayout()
        self.eo_table = QTableWidget(2, 6)
        self.eo_table.setHorizontalHeaderLabels([f"Cạnh {i}" for i in range(6)])
        self.eo_table.setVerticalHeaderLabels([f"Hàng {i+1}" for i in range(2)])
        eo_layout.addWidget(self.eo_table)
        eo_group.setLayout(eo_layout)
        tables_layout.addWidget(eo_group, 1, 1)
        
        config_layout.addLayout(tables_layout)
        
        # Initialize tables
        self.initialize_tables()
        
        config_group.setLayout(config_layout)
        left_layout.addWidget(config_group)
        
        # Algorithm selection
        algo_group = QGroupBox("Lựa chọn thuật toán")
        algo_layout = QVBoxLayout()
        
        self.algo_group = QButtonGroup()
        self.ac3_rb = QRadioButton("AC-3 (Arc Consistency)")
        self.ac3_rb.setChecked(True)
        self.backtracking_rb = QRadioButton("Backtracking")
        self.combined_rb = QRadioButton("AC-3 + Backtracking")
        
        self.algo_group.addButton(self.ac3_rb, 1)
        self.algo_group.addButton(self.backtracking_rb, 2)
        self.algo_group.addButton(self.combined_rb, 3)
        
        algo_layout.addWidget(self.ac3_rb)
        algo_layout.addWidget(self.backtracking_rb)
        algo_layout.addWidget(self.combined_rb)
        
        # Number of solutions to find
        solutions_layout = QHBoxLayout()
        solutions_layout.addWidget(QLabel("Số lượng giải pháp cần tìm:"))
        self.solutions_spinbox = QSpinBox()
        self.solutions_spinbox.setRange(1, 10)
        self.solutions_spinbox.setValue(3)
        solutions_layout.addWidget(self.solutions_spinbox)
        algo_layout.addLayout(solutions_layout)
        
        # Execute button
        self.execute_btn = QPushButton("Thực thi thuật toán")
        self.execute_btn.clicked.connect(self.execute_algorithm)
        algo_layout.addWidget(self.execute_btn)
        
        algo_group.setLayout(algo_layout)
        left_layout.addWidget(algo_group)
        
        # Right section - Results
        right_widget = QWidget()
        right_layout = QVBoxLayout()
        right_widget.setLayout(right_layout)
        
        # Domain display
        domain_group = QGroupBox("Miền giá trị sau khi áp dụng AC-3")
        domain_layout = QVBoxLayout()
        
        self.domain_text = QTextEdit()
        self.domain_text.setReadOnly(True)
        domain_layout.addWidget(self.domain_text)
        
        domain_group.setLayout(domain_layout)
        right_layout.addWidget(domain_group)
        
        # Results section
        results_group = QGroupBox("Kết quả")
        results_layout = QVBoxLayout()
        
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.result_text.setStyleSheet("QTextEdit { font-family: monospace; }")
        results_layout.addWidget(self.result_text)
        
        results_group.setLayout(results_layout)
        right_layout.addWidget(results_group)
        
        # Add left and right sections to splitter
        content_splitter.addWidget(left_widget)
        content_splitter.addWidget(right_widget)
        content_splitter.setSizes([600, 800])  # Initial sizes
    
    def initialize_tables(self):
        """Khởi tạo các bảng với các ô nhập liệu"""
        # Corner Permutation (cp) table
        for i in range(2):
            for j in range(4):
                idx = i * 4 + j
                combo = QComboBox()
                combo.addItem("")  # Empty option
                combo.addItems([str(x) for x in range(8)])
                self.cp_table.setCellWidget(i, j, combo)
        
        # Corner Orientation (co) table
        for i in range(2):
            for j in range(4):
                idx = i * 4 + j
                combo = QComboBox()
                combo.addItem("")  # Empty option
                combo.addItems([str(x) for x in range(3)])
                self.co_table.setCellWidget(i, j, combo)
        
        # Edge Permutation (ep) table
        for i in range(2):
            for j in range(6):
                idx = i * 6 + j
                combo = QComboBox()
                combo.addItem("")  # Empty option
                combo.addItems([str(x) for x in range(12)])
                self.ep_table.setCellWidget(i, j, combo)
        
        # Edge Orientation (eo) table
        for i in range(2):
            for j in range(6):
                idx = i * 6 + j
                combo = QComboBox()
                combo.addItem("")  # Empty option
                combo.addItems(["0", "1"])
                self.eo_table.setCellWidget(i, j, combo)
        
        # Resize columns to content
        for table in [self.cp_table, self.co_table, self.ep_table, self.eo_table]:
            table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            table.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
    
    def generate_empty_config(self):
        """Tạo cấu hình trống cho tất cả các bảng"""
        # Clear all selections
        for i in range(2):
            for j in range(4):
                self.cp_table.cellWidget(i, j).setCurrentIndex(0)
                self.co_table.cellWidget(i, j).setCurrentIndex(0)
        
        for i in range(2):
            for j in range(6):
                self.ep_table.cellWidget(i, j).setCurrentIndex(0)
                self.eo_table.cellWidget(i, j).setCurrentIndex(0)
        
        self.result_text.clear()
        self.domain_text.clear()
        self.domain_text.setText("Miền giá trị ban đầu chưa được thu hẹp.\nChạy thuật toán AC-3 để thấy kết quả.")
    
    def generate_partial_random(self):
        """Tạo cấu hình ngẫu nhiên một phần"""
        # Clear first
        self.generate_empty_config()
        
        # Set random values for ~30% of cells
        # Corner Permutation
        used_cp = set()
        for _ in range(2):  # Fill 2 random cp cells
            i, j = random.randint(0, 1), random.randint(0, 3)
            idx = i * 4 + j
            
            # Ensure unique values for cp
            val = random.randint(0, 7)
            while val in used_cp:
                val = random.randint(0, 7)
                
            used_cp.add(val)
            self.cp_table.cellWidget(i, j).setCurrentIndex(val + 1)  # +1 because index 0 is empty
        
        # Corner Orientation
        for _ in range(2):  # Fill 2 random co cells
            i, j = random.randint(0, 1), random.randint(0, 3)
            val = random.randint(0, 2)
            self.co_table.cellWidget(i, j).setCurrentIndex(val + 1)
        
        # Edge Permutation
        used_ep = set()
        for _ in range(3):  # Fill 3 random ep cells
            i, j = random.randint(0, 1), random.randint(0, 5)
            
            # Ensure unique values for ep
            val = random.randint(0, 11)
            while val in used_ep:
                val = random.randint(0, 11)
                
            used_ep.add(val)
            self.ep_table.cellWidget(i, j).setCurrentIndex(val + 1)
        
        # Edge Orientation
        for _ in range(3):  # Fill 3 random eo cells
            i, j = random.randint(0, 1), random.randint(0, 5)
            val = random.randint(0, 1)
            self.eo_table.cellWidget(i, j).setCurrentIndex(val + 1)
        
        self.domain_text.setText("Một số giá trị đã được thiết lập ngẫu nhiên.\nChạy thuật toán AC-3 để thu hẹp miền giá trị.")
    
    def generate_solved_state(self):
        """Thiết lập cấu hình trạng thái đã giải"""
        # Clear first
        self.generate_empty_config()
        
        # Set values to solved state
        for i in range(2):
            for j in range(4):
                idx = i * 4 + j
                if idx < 8:
                    # cp = ordered 0-7
                    self.cp_table.cellWidget(i, j).setCurrentIndex(idx + 1)
                    # co = all 0
                    self.co_table.cellWidget(i, j).setCurrentIndex(1)  # Index 1 = value 0
        
        for i in range(2):
            for j in range(6):
                idx = i * 6 + j
                if idx < 12:
                    # ep = ordered 0-11
                    self.ep_table.cellWidget(i, j).setCurrentIndex(idx + 1)
                    # eo = all 0
                    self.eo_table.cellWidget(i, j).setCurrentIndex(1)  # Index 1 = value 0
        
        self.domain_text.setText("Cấu hình đã giải được thiết lập.\nĐây là một cấu hình hoàn chỉnh và hợp lệ.")
    
    def get_current_configuration(self):
        """Lấy cấu hình hiện tại từ các bảng"""
        config = {
            "cp": [None] * 8,
            "co": [None] * 8,
            "ep": [None] * 12,
            "eo": [None] * 12
        }
        
        # Get corner permutation
        for i in range(2):
            for j in range(4):
                idx = i * 4 + j
                if idx < 8:
                    combo = self.cp_table.cellWidget(i, j)
                    text = combo.currentText()
                    if text:  # Not empty
                        config["cp"][idx] = int(text)
        
        # Get corner orientation
        for i in range(2):
            for j in range(4):
                idx = i * 4 + j
                if idx < 8:
                    combo = self.co_table.cellWidget(i, j)
                    text = combo.currentText()
                    if text:  # Not empty
                        config["co"][idx] = int(text)
        
        # Get edge permutation
        for i in range(2):
            for j in range(6):
                idx = i * 6 + j
                if idx < 12:
                    combo = self.ep_table.cellWidget(i, j)
                    text = combo.currentText()
                    if text:  # Not empty
                        config["ep"][idx] = int(text)
        
        # Get edge orientation
        for i in range(2):
            for j in range(6):
                idx = i * 6 + j
                if idx < 12:
                    combo = self.eo_table.cellWidget(i, j)
                    text = combo.currentText()
                    if text:  # Not empty
                        config["eo"][idx] = int(text)
        
        return config
    
    def calculate_parity(self, perm):
        """Tính dấu hoán vị (chẵn: 0, lẻ: 1)"""
        # Filter out None values
        valid_perm = [p for p in perm if p is not None]
        
        if len(valid_perm) <= 1:
            return 0  # Không đủ phần tử để tính parity
            
        inversions = 0
        for i in range(len(valid_perm)):
            for j in range(i + 1, len(valid_perm)):
                if valid_perm[i] > valid_perm[j]:
                    inversions += 1
        return inversions % 2
    
    def show_fine_tune_dialog(self):
        """Hiển thị hộp thoại để điều chỉnh cấu hình tinh chỉnh"""
        # Lấy cấu hình hiện tại
        rubik_state = self.parse_configuration()
        if not rubik_state:
            rubik_state = SOLVED_STATE_3x3  # Sử dụng trạng thái giải nếu không có cấu hình hợp lệ
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Điều chỉnh cấu hình tinh chỉnh")
        dialog.setMinimumWidth(700)
        
        layout = QVBoxLayout()
        dialog.setLayout(layout)
        
        # Tạo tabs cho từng loại điều chỉnh
        from PyQt5.QtWidgets import QTabWidget
        tab_widget = QTabWidget()
        layout.addWidget(tab_widget)
        
        # Tab điều chỉnh Corner Permutation (cp)
        cp_tab = QWidget()
        cp_layout = QGridLayout()
        cp_tab.setLayout(cp_layout)
        
        self.cp_spinboxes = []
        for i in range(8):
            label = QLabel(f"Góc {i}:")
            spinbox = QSpinBox()
            spinbox.setRange(0, 7)
            spinbox.setValue(rubik_state.cp[i] if i < len(rubik_state.cp) else i)
            self.cp_spinboxes.append(spinbox)
            cp_layout.addWidget(label, i // 4, (i % 4) * 2)
            cp_layout.addWidget(spinbox, i // 4, (i % 4) * 2 + 1)
        
        # Tab điều chỉnh Corner Orientation (co)
        co_tab = QWidget()
        co_layout = QGridLayout()
        co_tab.setLayout(co_layout)
        
        self.co_spinboxes = []
        for i in range(8):
            label = QLabel(f"Góc {i}:")
            spinbox = QSpinBox()
            spinbox.setRange(0, 2)
            spinbox.setValue(rubik_state.co[i] if i < len(rubik_state.co) else 0)
            self.co_spinboxes.append(spinbox)
            co_layout.addWidget(label, i // 4, (i % 4) * 2)
            co_layout.addWidget(spinbox, i // 4, (i % 4) * 2 + 1)
        
        # Tab điều chỉnh Edge Permutation (ep)
        ep_tab = QWidget()
        ep_layout = QGridLayout()
        ep_tab.setLayout(ep_layout)
        
        self.ep_spinboxes = []
        for i in range(12):
            label = QLabel(f"Cạnh {i}:")
            spinbox = QSpinBox()
            spinbox.setRange(0, 11)
            spinbox.setValue(rubik_state.ep[i] if i < len(rubik_state.ep) else i)
            self.ep_spinboxes.append(spinbox)
            ep_layout.addWidget(label, i // 6, (i % 6) * 2)
            ep_layout.addWidget(spinbox, i // 6, (i % 6) * 2 + 1)
        
        # Tab điều chỉnh Edge Orientation (eo)
        eo_tab = QWidget()
        eo_layout = QGridLayout()
        eo_tab.setLayout(eo_layout)
        
        self.eo_spinboxes = []
        for i in range(12):
            label = QLabel(f"Cạnh {i}:")
            spinbox = QSpinBox()
            spinbox.setRange(0, 1)
            spinbox.setValue(rubik_state.eo[i] if i < len(rubik_state.eo) else 0)
            self.eo_spinboxes.append(spinbox)
            eo_layout.addWidget(label, i // 6, (i % 6) * 2)
            eo_layout.addWidget(spinbox, i // 6, (i % 6) * 2 + 1)
        
        # Thêm các tab vào tab widget
        tab_widget.addTab(cp_tab, "Corner Permutation (cp)")
        tab_widget.addTab(co_tab, "Corner Orientation (co)")
        tab_widget.addTab(ep_tab, "Edge Permutation (ep)")
        tab_widget.addTab(eo_tab, "Edge Orientation (eo)")
        
        # Nút tự động điều chỉnh để đảm bảo ràng buộc
        adjust_btn = QPushButton("Điều chỉnh tự động để đảm bảo ràng buộc")
        adjust_btn.clicked.connect(self.auto_adjust_constraints)
        layout.addWidget(adjust_btn)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)
        
        if dialog.exec_():
            # Lấy giá trị từ các spinbox
            cp = tuple(spinbox.value() for spinbox in self.cp_spinboxes)
            co = tuple(spinbox.value() for spinbox in self.co_spinboxes)
            ep = tuple(spinbox.value() for spinbox in self.ep_spinboxes)
            eo = tuple(spinbox.value() for spinbox in self.eo_spinboxes)
            
            # Cập nhật vào ô nhập liệu
            new_state_text = f"RubikState(\n  cp={cp},\n  co={co},\n  ep={ep},\n  eo={eo}\n)"
            self.manual_input.setText(new_state_text)
            
            # Hiển thị trạng thái
            new_state = RubikState(cp, co, ep, eo)
            self.display_rubik_state(new_state)
            
    def auto_adjust_constraints(self):
        """Tự động điều chỉnh các giá trị để đảm bảo ràng buộc"""
        # Điều chỉnh tổng co chia hết cho 3
        co_values = [spinbox.value() for spinbox in self.co_spinboxes]
        co_sum = sum(co_values) % 3
        if co_sum != 0:
            # Điều chỉnh giá trị cuối cùng
            self.co_spinboxes[7].setValue((co_values[7] + (3 - co_sum)) % 3)
        
        # Điều chỉnh tổng eo chia hết cho 2
        eo_values = [spinbox.value() for spinbox in self.eo_spinboxes]
        if sum(eo_values) % 2 != 0:
            # Đảo bit cuối cùng
            self.eo_spinboxes[11].setValue(1 - eo_values[11])
        
        # Đảm bảo cp là hoán vị
        cp_values = [spinbox.value() for spinbox in self.cp_spinboxes]
        unique_cp = set(cp_values)
        if len(unique_cp) != 8:
            # Tìm các giá trị bị thiếu và trùng lặp
            missing = set(range(8)) - unique_cp
            duplicates = [i for i in range(8) if cp_values.count(i) > 1]
            
            # Điều chỉnh các giá trị trùng lặp thành các giá trị bị thiếu
            missing = list(missing)
            for i, val in enumerate(cp_values):
                if val in duplicates and missing:
                    # Thay đổi giá trị trùng lặp thành giá trị bị thiếu
                    new_val = missing.pop(0)
                    self.cp_spinboxes[i].setValue(new_val)
                    duplicates.remove(val) if duplicates.count(val) == 1 else duplicates
        
        # Đảm bảo ep là hoán vị
        ep_values = [spinbox.value() for spinbox in self.ep_spinboxes]
        unique_ep = set(ep_values)
        if len(unique_ep) != 12:
            # Tìm các giá trị bị thiếu và trùng lặp
            missing = set(range(12)) - unique_ep
            duplicates = [i for i in range(12) if ep_values.count(i) > 1]
            
            # Điều chỉnh các giá trị trùng lặp thành các giá trị bị thiếu
            missing = list(missing)
            for i, val in enumerate(ep_values):
                if val in duplicates and missing:
                    # Thay đổi giá trị trùng lặp thành giá trị bị thiếu
                    new_val = missing.pop(0)
                    self.ep_spinboxes[i].setValue(new_val)
                    duplicates.remove(val) if duplicates.count(val) == 1 else duplicates
                    
        # Đảm bảo corner parity và edge parity khớp nhau
        cp_values = [spinbox.value() for spinbox in self.cp_spinboxes]
        ep_values = [spinbox.value() for spinbox in self.ep_spinboxes]
        
        corner_parity = self.calculate_parity(cp_values)
        edge_parity = self.calculate_parity(ep_values)
        
        if corner_parity != edge_parity:
            # Hoán đổi hai cạnh để thay đổi parity
            self.ep_spinboxes[0].setValue(ep_values[1])
            self.ep_spinboxes[1].setValue(ep_values[0])
    
    def display_rubik_state(self, rubik_state):
        """Hiển thị trạng thái Rubik trong state_text"""
        if not rubik_state:
            self.state_text.setText("Không có trạng thái hợp lệ để hiển thị.")
            return
            
        display_text = "=== TRẠNG THÁI RUBIK HIỆN TẠI ===\n\n"
        display_text += f"Corner Permutation (cp):\n{rubik_state.cp}\n\n"
        display_text += f"Corner Orientation (co):\n{rubik_state.co}\n\n"
        display_text += f"Edge Permutation (ep):\n{rubik_state.ep}\n\n"
        display_text += f"Edge Orientation (eo):\n{rubik_state.eo}\n\n"
        
        # Thêm giải thích về cp, co, ep, eo
        display_text += "Chú thích:\n"
        display_text += "- cp: Hoán vị góc (0=URF, 1=ULF, 2=ULB, 3=URB, 4=DRF, 5=DLF, 6=DLB, 7=DRB)\n"
        display_text += "- co: Định hướng góc (0=đúng hướng, 1=xoay CW 120°, 2=xoay CW 240°)\n"
        display_text += "- ep: Hoán vị cạnh (0=UR, 1=UF, 2=UL, 3=UB, 4=DR, 5=DF, 6=DL, 7=DB, 8=FR, 9=FL, 10=BL, 11=BR)\n"
        display_text += "- eo: Định hướng cạnh (0=đúng hướng, 1=lật ngược)\n"
        
        self.state_text.setText(display_text)
    
    def parse_configuration(self):
        """Phân tích cấu hình từ văn bản nhập vào"""
        config_text = self.manual_input.toPlainText().strip()
        
        try:
            # Kiểm tra định dạng cơ bản
            if not config_text.startswith("RubikState"):
                self.result_text.setText("Lỗi: Cấu hình phải bắt đầu bằng 'RubikState'")
                return None
                
            # Đếm và kiểm tra cặp ngoặc đơn
            open_count = config_text.count('(')
            close_count = config_text.count(')')
            if open_count != close_count:
                self.result_text.setText(f"Lỗi: Số lượng dấu ngoặc đơn mở ({open_count}) và đóng ({close_count}) không khớp nhau.")
                return None
            
            # Tìm các tham số
            params = {}
            for param_name in ["cp", "co", "ep", "eo"]:
                param_value = self._extract_parameter(config_text, param_name)
                if param_value is None:
                    missing_params = [p for p in ["cp", "co", "ep", "eo"] if p not in params]
                    self.result_text.setText(f"Lỗi: Thiếu các tham số: {', '.join(missing_params)}")
                    return None
                params[param_name] = param_value
                
            # Tạo đối tượng RubikState
            try:
                # Chuyển đổi sang tuple nếu là list
                cp = tuple(params["cp"]) if isinstance(params["cp"], list) else params["cp"]
                co = tuple(params["co"]) if isinstance(params["co"], list) else params["co"]
                ep = tuple(params["ep"]) if isinstance(params["ep"], list) else params["ep"]
                eo = tuple(params["eo"]) if isinstance(params["eo"], list) else params["eo"]
                
                # Kiểm tra kiểu dữ liệu
                if not (isinstance(cp, tuple) and isinstance(co, tuple) and 
                        isinstance(ep, tuple) and isinstance(eo, tuple)):
                    self.result_text.setText("Lỗi: Các tham số phải là tuple hoặc list")
                    return None
                
                return RubikState(cp, co, ep, eo)
            except Exception as e:
                self.result_text.setText(f"Lỗi khi chuyển đổi tham số: {str(e)}")
                return None
                
        except Exception as e:
            self.result_text.setText(f"Lỗi khi phân tích cấu hình: {str(e)}")
            return None
    
    def _extract_parameter(self, config_text, param_name):
        """Trích xuất một tham số từ văn bản cấu hình"""
        param_start = config_text.find(f"{param_name}=")
        if param_start < 0:
            return None
            
        param_start += len(param_name) + 1  # Độ dài của "param_name="
        
        # Tìm dấu ngoặc mở đầu tiên sau param=
        open_paren = config_text.find("(", param_start)
        if open_paren >= 0:
            # Tìm dấu ngoặc đóng tương ứng
            depth = 1
            pos = open_paren + 1
            while pos < len(config_text) and depth > 0:
                if config_text[pos] == "(":
                    depth += 1
                elif config_text[pos] == ")":
                    depth -= 1
                pos += 1
            
            if depth == 0:  # Tìm thấy dấu ngoặc đóng tương ứng
                param_str = config_text[open_paren:pos]
            else:
                return None
        else:
            # Có thể là dạng không có ngoặc: param=0,1,2,3...
            param_end = config_text.find(",", param_start)
            if param_end < 0:
                param_end = config_text.find(")", param_start)
            if param_end > 0:
                param_str = "(" + config_text[param_start:param_end].strip() + ")"
            else:
                return None
                
        return self.safe_eval(param_str)
        
    def safe_eval(self, value_str):
        """Đánh giá an toàn một chuỗi thành đối tượng Python"""
        try:
            # Làm sạch chuỗi
            clean_str = value_str.strip()
            
            # Nếu là tuple rỗng
            if clean_str == "()" or clean_str == "[]":
                return tuple()
                
            # Nếu đã có dấu ngoặc, sử dụng eval trực tiếp
            if (clean_str.startswith("(") and clean_str.endswith(")")) or \
               (clean_str.startswith("[") and clean_str.endswith("]")):
                return eval(clean_str)
                
            # Nếu là danh sách giá trị phân cách bằng dấu phẩy mà không có ngoặc
            if "," in clean_str:
                values = [v.strip() for v in clean_str.split(",")]
                return tuple(int(v) for v in values if v)
                
            # Nếu chỉ là một số
            if clean_str.isdigit():
                return (int(clean_str),)
                
            # Mặc định
            return eval(clean_str)
        except Exception as e:
            raise ValueError(f"Không thể đánh giá chuỗi '{value_str}': {str(e)}")
    
    def execute_algorithm(self):
        """Thực thi thuật toán CSP đã chọn"""
        algorithm = self.get_selected_algorithm()
        
        # Lấy cấu hình hiện tại
        config = self.get_current_configuration()
        
        # Khởi tạo các biến và miền giá trị
        variables, domains = self.setup_csp_variables(config)
        
        # Thực thi thuật toán tương ứng
        if algorithm == "AC-3":
            self.run_ac3(variables, domains)
        elif algorithm == "Backtracking":
            self.run_backtracking(variables, domains)
        elif algorithm == "Combined":
            # Chạy AC-3 trước
            revised_domains = self.run_ac3(variables, domains, return_domains=True)
            # Sau đó chạy Backtracking với miền đã thu hẹp
            self.run_backtracking(variables, revised_domains)
    
    def get_selected_algorithm(self):
        """Lấy thuật toán đang được chọn"""
        if self.ac3_rb.isChecked():
            return "AC-3"
        elif self.backtracking_rb.isChecked():
            return "Backtracking"
        elif self.combined_rb.isChecked():
            return "Combined"
        return "Unknown"
    
    def setup_csp_variables(self, config):
        """Thiết lập các biến và miền giá trị dựa trên cấu hình"""
        variables = []
        domains = {}
        
        # Corner permutation variables
        for i in range(8):
            var_name = f"cp_{i}"
            variables.append(var_name)
            
            if config["cp"][i] is not None:
                domains[var_name] = [config["cp"][i]]
            else:
                # Domain contains all values not already used
                used_values = [v for v in config["cp"] if v is not None]
                domains[var_name] = [v for v in range(8) if v not in used_values]
        
        # Corner orientation variables
        for i in range(8):
            var_name = f"co_{i}"
            variables.append(var_name)
            
            if config["co"][i] is not None:
                domains[var_name] = [config["co"][i]]
            else:
                domains[var_name] = [0, 1, 2]
        
        # Edge permutation variables
        for i in range(12):
            var_name = f"ep_{i}"
            variables.append(var_name)
            
            if config["ep"][i] is not None:
                domains[var_name] = [config["ep"][i]]
            else:
                # Domain contains all values not already used
                used_values = [v for v in config["ep"] if v is not None]
                domains[var_name] = [v for v in range(12) if v not in used_values]
        
        # Edge orientation variables
        for i in range(12):
            var_name = f"eo_{i}"
            variables.append(var_name)
            
            if config["eo"][i] is not None:
                domains[var_name] = [config["eo"][i]]
            else:
                domains[var_name] = [0, 1]
        
        return variables, domains
    
    def run_ac3(self, variables, domains, return_domains=False):
        """Chạy thuật toán AC-3"""
        self.result_text.clear()
        self.domain_text.clear()
        
        # Copy domains to avoid modifying the original
        domains = {var: list(values) for var, values in domains.items()}
        
        # Setup constraints (arcs)
        constraints = []
        
        # Add constraints for corner permutation (alldiff)
        for i in range(8):
            for j in range(i + 1, 8):
                constraints.append((f"cp_{i}", f"cp_{j}"))
        
        # Add constraints for edge permutation (alldiff)
        for i in range(12):
            for j in range(i + 1, 12):
                constraints.append((f"ep_{i}", f"ep_{j}"))
        
        # Add constraints for corner orientation (sum mod 3 = 0)
        for i in range(8):
            for j in range(8):
                if i != j:
                    constraints.append((f"co_{i}", f"co_{j}"))
        
        # Add constraints for edge orientation (sum mod 2 = 0)
        for i in range(12):
            for j in range(12):
                if i != j:
                    constraints.append((f"eo_{i}", f"eo_{j}"))
        
        # Add constraints for parity match
        for i in range(8):
            for j in range(12):
                constraints.append((f"cp_{i}", f"ep_{j}"))
        
        # Initialize queue with all constraints
        queue = constraints.copy()
        
        # AC-3 algorithm
        result = "<h3>Thuật toán AC-3 (Arc Consistency):</h3>\n"
        result += "<p>AC-3 sẽ loại bỏ các giá trị không thỏa mãn ràng buộc từ miền của các biến.</p>\n"
        
        steps = []
        revisions = 0
        
        while queue:
            xi, xj = queue.pop(0)
            revision_made = False
            removed_values = []
            
            # Check if we need to revise the domain of xi
            for x in list(domains[xi]):  # Create a copy to avoid modifying during iteration
                # Check if there's a value in xj that satisfies the constraint
                satisfiable = False
                
                for y in domains[xj]:
                    if self.satisfies_constraint(xi, x, xj, y):
                        satisfiable = True
                        break
                
                if not satisfiable:
                    domains[xi].remove(x)
                    removed_values.append(x)
                    revision_made = True
            
            if revision_made:
                revisions += 1
                step = f"<p>- Xét ràng buộc ({xi}, {xj}): loại bỏ {removed_values} khỏi miền của {xi}</p>\n"
                steps.append(step)
                
                # Add neighboring arcs back to the queue
                for xk, xl in constraints:
                    if xl == xi and xk != xj:
                        queue.append((xk, xi))
                    elif xk == xi and xl != xj:
                        queue.append((xi, xl))
            
            # Check for empty domains
            if not domains[xi]:
                break
        
        # Display the revised domains
        domain_text = "<h3>Miền giá trị sau khi áp dụng AC-3:</h3>\n"
        
        # Group domains by type (cp, co, ep, eo)
        domain_types = {
            "cp": "<h4>Corner Permutation (cp):</h4>\n<ul>\n",
            "co": "<h4>Corner Orientation (co):</h4>\n<ul>\n",
            "ep": "<h4>Edge Permutation (ep):</h4>\n<ul>\n",
            "eo": "<h4>Edge Orientation (eo):</h4>\n<ul>\n"
        }
        
        for var in sorted(domains.keys()):
            var_type = var.split("_")[0]
            var_index = var.split("_")[1]
            domain_types[var_type] += f"<li>{var}: {domains[var]}</li>\n"
        
        for var_type in domain_types:
            domain_types[var_type] += "</ul>\n"
            domain_text += domain_types[var_type]
        
        # Update domain text
        self.domain_text.setHtml(domain_text)
        
        # Display AC-3 results
        result += f"<p>AC-3 đã thực hiện {revisions} lần sửa đổi miền.</p>\n"
        
        # Show steps
        result += "<h4>Các bước thực hiện:</h4>\n"
        for step in steps[:20]:  # Limit to 20 steps for display
            result += step
        
        if len(steps) > 20:
            result += f"<p><i>...và {len(steps) - 20} bước khác</i></p>\n"
        
        # Check for empty domains
        empty_domains = [var for var, domain in domains.items() if not domain]
        if empty_domains:
            result += "<h4>Kết quả:</h4>\n"
            result += f"<p style='color:red'>❌ Không tìm thấy giải pháp. Các biến sau có miền rỗng: {empty_domains}</p>\n"
        else:
            result += "<h4>Kết quả:</h4>\n"
            fixed_vars = sum(1 for domain in domains.values() if len(domain) == 1)
            result += f"<p style='color:green'>✓ AC-3 hoàn thành. {fixed_vars}/{len(variables)} biến đã xác định đầy đủ.</p>\n"
            
            # Check if all variables are fixed
            if fixed_vars == len(variables):
                result += "<p>Đã tìm thấy một giải pháp hoàn chỉnh!</p>\n"
                
                # Extract the solution
                solution = {}
                for var, domain in domains.items():
                    solution[var] = domain[0]
                
                # Verify the solution
                is_valid = self.verify_solution(solution)
                if is_valid:
                    result += "<p style='color:green'>✓ Giải pháp thỏa mãn tất cả các ràng buộc!</p>\n"
                else:
                    result += "<p style='color:red'>❌ Giải pháp không thỏa mãn tất cả các ràng buộc.</p>\n"
                
                # Display the solution
                result += self.format_solution(solution)
        
        self.result_text.setHtml(result)
        
        if return_domains:
            return domains
    
    def run_backtracking(self, variables, domains, max_solutions=None):
        """Chạy thuật toán Backtracking để tìm các giải pháp"""
        self.result_text.clear()
        if not self.backtracking_rb.isChecked():  # If combined mode, don't clear domain text
            self.domain_text.clear()
        
        # Copy domains to avoid modifying the original
        domains = {var: list(values) for var, values in domains.items()}
        
        if max_solutions is None:
            max_solutions = self.solutions_spinbox.value()
        
        result = "<h3>Thuật toán Backtracking:</h3>\n"
        result += f"<p>Tìm tối đa {max_solutions} giải pháp thỏa mãn tất cả các ràng buộc.</p>\n"
        
        # Backtracking algorithm
        solutions = []
        steps = []
        
        def backtrack(assignment, level=0):
            if len(solutions) >= max_solutions:
                return
            
            if len(assignment) == len(variables):
                # Found a solution
                solutions.append(assignment.copy())
                return
            
            # Choose variable with minimum remaining values (MRV)
            unassigned = [v for v in variables if v not in assignment]
            var = min(unassigned, key=lambda v: len(domains[v]))
            
            # Try each value in the domain
            for value in domains[var]:
                # Check if value is consistent with current assignment
                if self.is_consistent(var, value, assignment):
                    # Add to assignment
                    assignment[var] = value
                    steps.append(f"<p>{'&nbsp;' * level * 2}- Gán {var} = {value} (mức {level})</p>\n")
                    
                    # Recursive call
                    backtrack(assignment, level + 1)
                    
                    # Backtrack
                    if len(solutions) < max_solutions:
                        assignment.pop(var)
                        steps.append(f"<p>{'&nbsp;' * level * 2}- <i>Quay lui từ {var} = {value}</i></p>\n")
        
        # Start backtracking with empty assignment
        backtrack({})
        
        # Display the results
        if not steps:
            result += "<p>Không có bước nào được thực hiện. Có thể các miền giá trị ban đầu không hợp lệ.</p>\n"
        else:
            result += "<h4>Các bước thực hiện:</h4>\n"
            for step in steps[:30]:  # Limit to 30 steps for display
                result += step
            
            if len(steps) > 30:
                result += f"<p><i>...và {len(steps) - 30} bước khác</i></p>\n"
        
        result += f"<h4>Tìm thấy {len(solutions)} giải pháp:</h4>\n"
        
        if not solutions:
            result += "<p style='color:red'>❌ Không tìm thấy giải pháp thỏa mãn.</p>\n"
        else:
            for i, solution in enumerate(solutions):
                result += f"<h5>Giải pháp {i+1}:</h5>\n"
                result += self.format_solution(solution)
        
        self.result_text.setHtml(result)
    
    def satisfies_constraint(self, xi, x, xj, y):
        """Kiểm tra xem hai biến và giá trị có thỏa mãn ràng buộc không"""
        # Extract variable types and indices
        xi_type, xi_idx = xi.split('_')
        xj_type, xj_idx = xj.split('_')
        xi_idx, xj_idx = int(xi_idx), int(xj_idx)
        
        # Alldiff constraint for corner permutation
        if xi_type == 'cp' and xj_type == 'cp':
            return x != y
        
        # Alldiff constraint for edge permutation
        if xi_type == 'ep' and xj_type == 'ep':
            return x != y
        
        # For corner and edge orientation, we can't fully validate the sum constraint
        # with just two variables, but we can still allow any consistent assignment
        
        # For parity constraint, we would need the complete assignments
        # We'll implement a simplified check in is_consistent for the full assignment
        
        return True
    
    def is_consistent(self, var, value, assignment):
        """Kiểm tra xem giá trị của biến có nhất quán với các giá trị đã gán không"""
        var_type, var_idx = var.split('_')
        var_idx = int(var_idx)
        
        # Check alldiff constraints
        if var_type == 'cp':
            for other_var, other_val in assignment.items():
                if other_var.startswith('cp_') and other_val == value:
                    return False
        
        if var_type == 'ep':
            for other_var, other_val in assignment.items():
                if other_var.startswith('ep_') and other_val == value:
                    return False
        
        # Check corner orientation sum constraint
        if var_type == 'co' and var_idx == 7:  # Last corner orientation variable
            co_vars = [f"co_{i}" for i in range(8)]
            if all(co_var in assignment or co_var == var for co_var in co_vars):
                # Calculate sum of corner orientations
                co_sum = sum(assignment.get(co_var, 0) for co_var in co_vars if co_var != var) + value
                if co_sum % 3 != 0:
                    return False
        
        # Check edge orientation sum constraint
        if var_type == 'eo' and var_idx == 11:  # Last edge orientation variable
            eo_vars = [f"eo_{i}" for i in range(12)]
            if all(eo_var in assignment or eo_var == var for eo_var in eo_vars):
                # Calculate sum of edge orientations
                eo_sum = sum(assignment.get(eo_var, 0) for eo_var in eo_vars if eo_var != var) + value
                if eo_sum % 2 != 0:
                    return False
        
        # Check parity constraint if all corner and edge permutations are assigned
        cp_vars = [f"cp_{i}" for i in range(8)]
        ep_vars = [f"ep_{i}" for i in range(12)]
        
        if ((var_type == 'cp' and var_idx == 7) or (var_type == 'ep' and var_idx == 11)) and \
           all(cp_var in assignment or (cp_var == var and var_type == 'cp') for cp_var in cp_vars) and \
           all(ep_var in assignment or (ep_var == var and var_type == 'ep') for ep_var in ep_vars):
            
            # Extract corner and edge permutations
            cp_values = [assignment.get(f"cp_{i}", value if var == f"cp_{i}" else None) for i in range(8)]
            ep_values = [assignment.get(f"ep_{i}", value if var == f"ep_{i}" else None) for i in range(12)]
            
            # Only check parity if we have enough values
            if all(cp_values) and all(ep_values):
                cp_parity = self.calculate_parity(cp_values)
                ep_parity = self.calculate_parity(ep_values)
                
                if cp_parity != ep_parity:
                    return False
        
        return True
    
    def verify_solution(self, solution):
        """Verify if a solution satisfies all constraints"""
        # Extract corner and edge permutations and orientations
        cp = [solution[f"cp_{i}"] for i in range(8)]
        co = [solution[f"co_{i}"] for i in range(8)]
        ep = [solution[f"ep_{i}"] for i in range(12)]
        eo = [solution[f"eo_{i}"] for i in range(12)]
        
        # Check permutation constraints
        if len(set(cp)) != 8 or set(cp) != set(range(8)):
            return False
        
        if len(set(ep)) != 12 or set(ep) != set(range(12)):
            return False
        
        # Check orientation constraints
        if sum(co) % 3 != 0:
            return False
        
        if sum(eo) % 2 != 0:
            return False
        
        # Check parity constraint
        cp_parity = self.calculate_parity(cp)
        ep_parity = self.calculate_parity(ep)
        
        return cp_parity == ep_parity
    
    def format_solution(self, solution):
        """Format a solution for display"""
        # Extract cp, co, ep, eo
        cp = [solution.get(f"cp_{i}", None) for i in range(8)]
        co = [solution.get(f"co_{i}", None) for i in range(8)]
        ep = [solution.get(f"ep_{i}", None) for i in range(12)]
        eo = [solution.get(f"eo_{i}", None) for i in range(12)]
        
        # Format the solution
        result = "<div style='margin-left:20px'>\n"
        result += f"<p><b>cp</b> = {cp}</p>\n"
        result += f"<p><b>co</b> = {co}</p>\n"
        result += f"<p><b>ep</b> = {ep}</p>\n"
        result += f"<p><b>eo</b> = {eo}</p>\n"
        result += "</div>\n"
        
        return result 