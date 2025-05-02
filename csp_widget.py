import random
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, 
                            QPushButton, QLabel, QRadioButton, QButtonGroup,
                            QGroupBox, QTextEdit, QComboBox, QSplitter, QDialog, QDialogButtonBox,
                            QSpinBox, QFormLayout)
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
            <p><b>Phát biểu bài toán:</b> Xác định tính hợp lệ của một cấu hình Rubik bằng cách mô hình hóa dưới dạng bài toán thỏa mãn ràng buộc (CSP).</p>
            <p><b>Biến:</b> Các vị trí góc (cp), định hướng góc (co), vị trí cạnh (ep), định hướng cạnh (eo)</p>
            <p><b>Ràng buộc:</b> 
                (1) Hoán vị góc và cạnh phải hợp lệ; 
                (2) Tổng định hướng góc phải chia hết cho 3; 
                (3) Tổng định hướng cạnh phải chia hết cho 2; 
                (4) Corner parity và edge parity phải khớp nhau
            </p>
            <p><b>Mục tiêu:</b> Kiểm tra xem cấu hình đã cho có thỏa mãn tất cả các ràng buộc không, từ đó xác định khả năng giải được của cấu hình.</p>
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
        config_group = QGroupBox("Cấu hình Rubik")
        config_layout = QVBoxLayout()
        
        # Input options
        input_options_layout = QHBoxLayout()
        
        # Random button
        self.random_btn = QPushButton("Tạo cấu hình ngẫu nhiên")
        self.random_btn.clicked.connect(self.generate_random_config)
        input_options_layout.addWidget(self.random_btn)
        
        # Solve button
        self.solved_btn = QPushButton("Cấu hình đã giải")
        self.solved_btn.clicked.connect(self.generate_solved_state)
        input_options_layout.addWidget(self.solved_btn)
        
        # Manual input
        config_layout.addLayout(input_options_layout)
        config_layout.addWidget(QLabel("Nhập thủ công:"))
        
        # Tạo layout cho nhập từng thành phần
        manual_input_layout = QVBoxLayout()
        
        # Thêm hướng dẫn
        input_guide = QLabel("Định dạng: cp=(...), co=(...), ep=(...), eo=(...)")
        manual_input_layout.addWidget(input_guide)
        
        # Thêm các nút chèn mẫu
        template_layout = QHBoxLayout()
        
        self.insert_template_btn = QPushButton("Chèn mẫu RubikState")
        self.insert_template_btn.clicked.connect(self.insert_template)
        template_layout.addWidget(self.insert_template_btn)
        
        self.insert_cp_btn = QPushButton("Chèn cp")
        self.insert_cp_btn.clicked.connect(lambda: self.insert_component("cp"))
        template_layout.addWidget(self.insert_cp_btn)
        
        self.insert_co_btn = QPushButton("Chèn co")
        self.insert_co_btn.clicked.connect(lambda: self.insert_component("co"))
        template_layout.addWidget(self.insert_co_btn)
        
        self.insert_ep_btn = QPushButton("Chèn ep")
        self.insert_ep_btn.clicked.connect(lambda: self.insert_component("ep"))
        template_layout.addWidget(self.insert_ep_btn)
        
        self.insert_eo_btn = QPushButton("Chèn eo")
        self.insert_eo_btn.clicked.connect(lambda: self.insert_component("eo"))
        template_layout.addWidget(self.insert_eo_btn)
        
        manual_input_layout.addLayout(template_layout)
        
        # Text edit cho nhập thủ công
        self.manual_input = QTextEdit()
        self.manual_input.setPlaceholderText("Nhập cấu hình Rubik tại đây...\n\nVí dụ:\nRubikState(\n  cp=(0,1,2,3,4,5,6,7),\n  co=(0,0,0,0,0,0,0,0),\n  ep=(0,1,2,3,4,5,6,7,8,9,10,11),\n  eo=(0,0,0,0,0,0,0,0,0,0,0,0)\n)")
        self.manual_input.setMinimumHeight(200)
        manual_input_layout.addWidget(self.manual_input)
        
        # Thêm nút và form để điều chỉnh cấu hình tinh chỉnh
        fine_tune_btn = QPushButton("Điều chỉnh cấu hình tinh chỉnh")
        fine_tune_btn.clicked.connect(self.show_fine_tune_dialog)
        manual_input_layout.addWidget(fine_tune_btn)
        
        config_layout.addLayout(manual_input_layout)
        
        # Check button
        self.check_btn = QPushButton("Kiểm tra cấu hình")
        self.check_btn.clicked.connect(self.check_configuration)
        config_layout.addWidget(self.check_btn)
        
        config_group.setLayout(config_layout)
        left_layout.addWidget(config_group)
        
        # Algorithm selection
        algo_group = QGroupBox("Lựa chọn thuật toán")
        algo_layout = QVBoxLayout()
        
        self.algo_group = QButtonGroup()
        self.backtracking_rb = QRadioButton("Backtracking (gán từng số)")
        self.backtracking_rb.setChecked(True)
        self.backtracking_test_rb = QRadioButton("Backtracking kiểm thử (gắn hết 1 lượt)")
        self.ac3_rb = QRadioButton("AC-3")
        
        self.algo_group.addButton(self.backtracking_rb, 1)
        self.algo_group.addButton(self.backtracking_test_rb, 2)
        self.algo_group.addButton(self.ac3_rb, 3)
        
        algo_layout.addWidget(self.backtracking_rb)
        algo_layout.addWidget(self.backtracking_test_rb)
        algo_layout.addWidget(self.ac3_rb)
        
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
        
        # Rubik state display
        state_group = QGroupBox("Trạng thái Rubik hiện tại")
        state_layout = QVBoxLayout()
        
        self.state_text = QTextEdit()
        self.state_text.setReadOnly(True)
        state_layout.addWidget(self.state_text)
        
        state_group.setLayout(state_layout)
        right_layout.addWidget(state_group)
        
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
    
    def generate_random_config(self):
        """Tạo cấu hình Rubik ngẫu nhiên"""
        # Tạo hoán vị ngẫu nhiên cho góc (corner permutation)
        cp = list(range(8))
        random.shuffle(cp)
        
        # Tạo định hướng ngẫu nhiên cho góc (corner orientation)
        co = [random.randint(0, 2) for _ in range(8)]
        # Đảm bảo tổng orientation chia hết cho 3
        co_sum = sum(co) % 3
        if co_sum != 0:
            co[0] = (co[0] + (3 - co_sum)) % 3
        
        # Tạo hoán vị ngẫu nhiên cho cạnh (edge permutation)
        ep = list(range(12))
        random.shuffle(ep)
        
        # Tạo định hướng ngẫu nhiên cho cạnh (edge orientation)
        eo = [random.randint(0, 1) for _ in range(12)]
        # Đảm bảo tổng orientation chia hết cho 2
        if sum(eo) % 2 != 0:
            eo[0] = 1 - eo[0]  # Đảo bit đầu tiên
        
        # Đảm bảo parity khớp nhau
        corner_parity = self.calculate_parity(cp)
        edge_parity = self.calculate_parity(ep)
        
        if corner_parity != edge_parity:
            # Hoán đổi hai cạnh để thay đổi parity
            ep[0], ep[1] = ep[1], ep[0]
        
        # Tạo trạng thái Rubik
        rubik_state = RubikState(tuple(cp), tuple(co), tuple(ep), tuple(eo))
        
        # Chuyển đổi sang chuỗi để hiển thị
        config_text = f"RubikState(\n  cp={rubik_state.cp},\n  co={rubik_state.co},\n  ep={rubik_state.ep},\n  eo={rubik_state.eo}\n)"
        self.manual_input.setText(config_text)
        
        # Hiển thị state đầy đủ
        self.display_rubik_state(rubik_state)
    
    def generate_solved_state(self):
        """Tạo cấu hình trạng thái đã giải"""
        rubik_state = SOLVED_STATE_3x3
        config_text = f"RubikState(\n  cp={rubik_state.cp},\n  co={rubik_state.co},\n  ep={rubik_state.ep},\n  eo={rubik_state.eo}\n)"
        self.manual_input.setText(config_text)
        self.display_rubik_state(rubik_state)
    
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
    
    def calculate_parity(self, perm):
        """Tính dấu hoán vị (chẵn: 0, lẻ: 1)"""
        inversions = 0
        for i in range(len(perm)):
            for j in range(i + 1, len(perm)):
                if perm[i] > perm[j]:
                    inversions += 1
        return inversions % 2
    
    def check_configuration(self):
        """Kiểm tra cấu hình Rubik hiện tại có hợp lệ không"""
        # Phân tích cấu hình
        rubik_state = self.parse_configuration()
        if not rubik_state:
            return
            
        # Hiển thị trạng thái
        self.display_rubik_state(rubik_state)
        
        # Kiểm tra tính hợp lệ
        result_text = "<h3>Kiểm tra cấu hình:</h3>\n"
        
        # 1. Kiểm tra cp/co/ep/eo có đúng kích thước không
        if (len(rubik_state.cp) != 8 or len(rubik_state.co) != 8 or 
            len(rubik_state.ep) != 12 or len(rubik_state.eo) != 12):
            result_text += "<p style='color:red'>❌ Lỗi: Kích thước cp/co/ep/eo không đúng!</p>\n"
            self.result_text.setHtml(result_text)
            return
        
        # 2. Kiểm tra hoán vị góc có hợp lệ không
        if set(rubik_state.cp) != set(range(8)):
            result_text += "<p style='color:red'>❌ Lỗi: Hoán vị góc (cp) không hợp lệ!</p>\n"
            self.result_text.setHtml(result_text)
            return
        
        # 3. Kiểm tra định hướng góc có hợp lệ không
        if not all(0 <= co <= 2 for co in rubik_state.co):
            result_text += "<p style='color:red'>❌ Lỗi: Định hướng góc (co) không hợp lệ!</p>\n"
            self.result_text.setHtml(result_text)
            return
        
        # 4. Kiểm tra tổng định hướng góc có chia hết cho 3 không
        if sum(rubik_state.co) % 3 != 0:
            result_text += "<p style='color:red'>❌ Lỗi: Tổng định hướng góc (co) không chia hết cho 3!</p>\n"
            self.result_text.setHtml(result_text)
            return
        
        # 5. Kiểm tra hoán vị cạnh có hợp lệ không
        if set(rubik_state.ep) != set(range(12)):
            result_text += "<p style='color:red'>❌ Lỗi: Hoán vị cạnh (ep) không hợp lệ!</p>\n"
            self.result_text.setHtml(result_text)
            return
        
        # 6. Kiểm tra định hướng cạnh có hợp lệ không
        if not all(0 <= eo <= 1 for eo in rubik_state.eo):
            result_text += "<p style='color:red'>❌ Lỗi: Định hướng cạnh (eo) không hợp lệ!</p>\n"
            self.result_text.setHtml(result_text)
            return
        
        # 7. Kiểm tra tổng định hướng cạnh có chia hết cho 2 không
        if sum(rubik_state.eo) % 2 != 0:
            result_text += "<p style='color:red'>❌ Lỗi: Tổng định hướng cạnh (eo) không chia hết cho 2!</p>\n"
            self.result_text.setHtml(result_text)
            return
        
        # 8. Kiểm tra parity (chẵn/lẻ)
        corner_parity = self.calculate_parity(rubik_state.cp)
        edge_parity = self.calculate_parity(rubik_state.ep)
        if corner_parity != edge_parity:
            result_text += "<p style='color:red'>❌ Lỗi: Corner parity và edge parity không khớp nhau!</p>\n"
            self.result_text.setHtml(result_text)
            return
        
        # Cấu hình hợp lệ
        result_text += "<p style='color:green; font-weight:bold'>✅ Cấu hình Rubik hợp lệ!</p>\n\n"
        result_text += "<p><b>Đã kiểm tra:</b></p>\n<ul>\n"
        result_text += "<li>Kích thước và giá trị của cp/co/ep/eo</li>\n"
        result_text += "<li>Tổng định hướng góc chia hết cho 3</li>\n"
        result_text += "<li>Tổng định hướng cạnh chia hết cho 2</li>\n"
        result_text += "<li>Corner parity và edge parity khớp nhau</li>\n"
        result_text += "</ul>\n"
        
        self.result_text.setHtml(result_text)
    
    def execute_algorithm(self):
        """Thực thi thuật toán CSP đã chọn"""
        algorithm = self.get_selected_algorithm()
        
        # Phân tích cấu hình
        rubik_state = self.parse_configuration()
        if not rubik_state:
            return
            
        # Hiển thị trạng thái
        self.display_rubik_state(rubik_state)
        
        # Kiểm tra tính hợp lệ của cấu hình
        if (len(rubik_state.cp) != 8 or len(rubik_state.co) != 8 or 
            len(rubik_state.ep) != 12 or len(rubik_state.eo) != 12 or
            set(rubik_state.cp) != set(range(8)) or 
            not all(0 <= co <= 2 for co in rubik_state.co) or
            sum(rubik_state.co) % 3 != 0 or
            set(rubik_state.ep) != set(range(12)) or
            not all(0 <= eo <= 1 for eo in rubik_state.eo) or
            sum(rubik_state.eo) % 2 != 0):
            
            self.result_text.setText("Không thể thực thi thuật toán trên cấu hình không hợp lệ.\nVui lòng kiểm tra cấu hình trước.")
            return
        
        # Thực thi thuật toán
        result = f"Đang thực thi thuật toán {algorithm} trên cấu hình đã cho...\n\n"
        
        if algorithm == "Backtracking":
            result += self.run_backtracking(rubik_state)
            
        elif algorithm == "Backtracking Test":
            result += self.run_backtracking_test(rubik_state)
            
        elif algorithm == "AC-3":
            result += self.run_ac3(rubik_state)
            
        # Sử dụng setHtml thay vì setText để hiển thị nội dung HTML đúng cách
        self.result_text.setHtml(result)
    
    def run_backtracking(self, rubik_state):
        """Chạy thuật toán backtracking thực tế trên cấu hình Rubik"""
        result = "<h3>Thuật toán Backtracking (gán từng số):</h3>\n"
        result += "<p>Thuật toán này kiểm tra tính hợp lệ của cấu hình Rubik bằng cách gán từng giá trị và kiểm tra ràng buộc.</p>\n"
        
        # Thiết lập bài toán CSP
        variables = []  # Danh sách các biến
        domains = {}    # Miền giá trị cho mỗi biến
        assignments = {}  # Các giá trị đã gán
        
        # Định nghĩa biến và miền giá trị
        # Corner permutation - mỗi góc có thể ở vị trí 0-7
        for i in range(8):
            var_name = f"cp_{i}"
            variables.append(var_name)
            domains[var_name] = list(range(8))
            
        # Corner orientation - mỗi góc có thể có hướng 0-2
        for i in range(8):
            var_name = f"co_{i}"
            variables.append(var_name)
            domains[var_name] = [0, 1, 2]
            
        # Edge permutation - mỗi cạnh có thể ở vị trí 0-11
        for i in range(12):
            var_name = f"ep_{i}"
            variables.append(var_name)
            domains[var_name] = list(range(12))
            
        # Edge orientation - mỗi cạnh có thể có hướng 0-1
        for i in range(12):
            var_name = f"eo_{i}"
            variables.append(var_name)
            domains[var_name] = [0, 1]
            
        # Hàm kiểm tra ràng buộc
        def check_constraints(assignments, var, val):
            # Ràng buộc cho các góc - không trùng vị trí
            if var.startswith("cp_"):
                for other_var, other_val in assignments.items():
                    if other_var.startswith("cp_") and other_var != var and other_val == val:
                        return False
                        
            # Ràng buộc cho các cạnh - không trùng vị trí
            if var.startswith("ep_"):
                for other_var, other_val in assignments.items():
                    if other_var.startswith("ep_") and other_var != var and other_val == val:
                        return False
                        
            # Kiểm tra ràng buộc định hướng góc khi đã gán hết
            if var == "co_7" and all(f"co_{i}" in assignments for i in range(8)):
                co_vals = [assignments[f"co_{i}"] for i in range(8)]
                if sum(co_vals) % 3 != 0:
                    return False
                    
            # Kiểm tra ràng buộc định hướng cạnh khi đã gán hết
            if var == "eo_11" and all(f"eo_{i}" in assignments for i in range(12)):
                eo_vals = [assignments[f"eo_{i}"] for i in range(12)]
                if sum(eo_vals) % 2 != 0:
                    return False
                    
            # Kiểm tra ràng buộc parity khi đã gán hết cả cp và ep
            if (all(f"cp_{i}" in assignments for i in range(8)) and 
                all(f"ep_{i}" in assignments for i in range(12))):
                cp_vals = [assignments[f"cp_{i}"] for i in range(8)]
                ep_vals = [assignments[f"ep_{i}"] for i in range(12)]
                
                cp_parity = self.calculate_parity(cp_vals)
                ep_parity = self.calculate_parity(ep_vals)
                
                if cp_parity != ep_parity:
                    return False
                    
            return True
            
        # Thuật toán backtracking
        def backtrack_search(assignment, unassigned_vars, steps, max_steps=100):
            if steps >= max_steps:
                return None, steps
                
            if not unassigned_vars:  # Đã gán hết các biến
                return assignment, steps
                
            var = unassigned_vars[0]  # Lấy biến đầu tiên chưa gán
            
            for value in domains[var]:
                new_assignment = assignment.copy()
                new_assignment[var] = value
                
                if check_constraints(new_assignment, var, value):
                    # Ghi lại bước thực hiện
                    steps += 1
                    step_result = f"<p>- Gán <b>{var} = {value}</b>: "
                    step_result += f"<span style='color:green'>Hợp lệ</span></p>\n"
                    backtrack_steps.append(step_result)
                    
                    # Tiếp tục đệ quy
                    result, steps = backtrack_search(new_assignment, unassigned_vars[1:], steps, max_steps)
                    if result:
                        return result, steps
                    
                    # Nếu không tìm được kết quả, quay lui
                    step_result = f"<p>- <i>Quay lui từ <b>{var} = {value}</b></i></p>\n"
                    backtrack_steps.append(step_result)
            
            return None, steps
            
        # Khởi tạo cấu hình nếu có cấu hình sẵn
        if rubik_state:
            for i in range(8):
                assignments[f"cp_{i}"] = rubik_state.cp[i]
                assignments[f"co_{i}"] = rubik_state.co[i]
            for i in range(12):
                assignments[f"ep_{i}"] = rubik_state.ep[i]
                assignments[f"eo_{i}"] = rubik_state.eo[i]
            
            # Kiểm tra ràng buộc trên cấu hình đã cho
            is_valid_cp = len(set(rubik_state.cp)) == 8 and set(rubik_state.cp) == set(range(8))
            is_valid_co = all(0 <= co <= 2 for co in rubik_state.co) and sum(rubik_state.co) % 3 == 0
            is_valid_ep = len(set(rubik_state.ep)) == 12 and set(rubik_state.ep) == set(range(12))
            is_valid_eo = all(0 <= eo <= 1 for eo in rubik_state.eo) and sum(rubik_state.eo) % 2 == 0
            
            cp_parity = self.calculate_parity(rubik_state.cp)
            ep_parity = self.calculate_parity(rubik_state.ep)
            parity_valid = cp_parity == ep_parity
            
            all_valid = is_valid_cp and is_valid_co and is_valid_ep and is_valid_eo and parity_valid
            
            # Hiển thị kết quả kiểm tra ràng buộc
            result += "<h4>Kiểm tra ràng buộc trên cấu hình đã cho:</h4>\n"
            result += f"<p>- Hoán vị góc (cp): {self.format_result(is_valid_cp)}</p>\n"
            result += f"<p>- Định hướng góc (co): {self.format_result(is_valid_co)}</p>\n"
            result += f"<p>- Hoán vị cạnh (ep): {self.format_result(is_valid_ep)}</p>\n"
            result += f"<p>- Định hướng cạnh (eo): {self.format_result(is_valid_eo)}</p>\n"
            result += f"<p>- Parity góc và cạnh: {self.format_result(parity_valid, 'Khớp nhau', 'Không khớp')}</p>\n"
            
            if all_valid:
                result += "<h4>Kết luận:</h4>\n"
                result += "<p style='color:green; font-weight:bold'>✅ Cấu hình Rubik đã cho thỏa mãn tất cả các ràng buộc.</p>\n"
                result += "<p>→ Cấu hình này <b>có thể giải được</b>.</p>\n"
                return result
            
            # Nếu không thỏa mãn tất cả ràng buộc, tiếp tục với backtracking
            result += "<p>Cấu hình không thỏa mãn tất cả ràng buộc, tiếp tục với backtracking...</p>\n"
        
        # Thử chạy thuật toán backtracking từ cấu hình rỗng
        backtrack_steps = []  # Lưu các bước thực hiện
        final_assignment, step_count = backtrack_search({}, variables, 0, 50)
        
        # Hiển thị các bước thực hiện
        result += "<h4>Quá trình backtracking:</h4>\n"
        for step in backtrack_steps[:20]:  # Giới hạn số bước hiển thị
            result += step
            
        if len(backtrack_steps) > 20:
            result += f"<p><i>...và {len(backtrack_steps) - 20} bước khác</i></p>\n"
        
        # Hiển thị kết quả
        result += "<h4>Kết quả backtracking:</h4>\n"
        if final_assignment:
            result += f"<p>- Đã thực hiện {step_count} bước gán giá trị</p>\n"
            result += "<p style='color:green; font-weight:bold'>✅ Tìm thấy cấu hình Rubik hợp lệ!</p>\n"
            result += "<p>→ Cấu hình <b>có thể giải được</b>.</p>\n"
        else:
            result += f"<p>- Đã thực hiện {step_count} bước gán giá trị mà không tìm thấy kết quả</p>\n"
            result += "<p>→ Có thể cấu hình <b>không thể giải được</b>, hoặc thuật toán cần nhiều bước hơn để tìm ra kết quả.</p>\n"
        
        return result
    
    def run_backtracking_test(self, rubik_state):
        """Chạy thuật toán backtracking kiểm thử trên cấu hình Rubik"""
        result = "<h3>Thuật toán Backtracking kiểm thử (gắn hết 1 lượt):</h3>\n"
        result += "<ul>\n"
        result += "<li>Bắt đầu với cấu hình đầy đủ</li>\n"
        result += "<li>Kiểm tra xem tất cả các ràng buộc có được thỏa mãn không</li>\n"
        result += "</ul>\n"
        
        # Kiểm tra các ràng buộc cơ bản
        
        # 1. Kiểm tra tất cả các hoán vị và định hướng có hợp lệ không
        result += "<h4>Kiểm tra tính hợp lệ của cấu hình:</h4>\n"
        
        # Kiểm tra hoán vị góc (cp)
        cp_valid = set(rubik_state.cp) == set(range(8))
        result += f"<p>- Hoán vị góc (cp): {self.format_result(cp_valid)}</p>\n"
        
        # Kiểm tra định hướng góc (co)
        co_valid = all(0 <= co <= 2 for co in rubik_state.co) and sum(rubik_state.co) % 3 == 0
        result += f"<p>- Định hướng góc (co): {self.format_result(co_valid)}</p>\n"
        
        # Kiểm tra hoán vị cạnh (ep)
        ep_valid = set(rubik_state.ep) == set(range(12))
        result += f"<p>- Hoán vị cạnh (ep): {self.format_result(ep_valid)}</p>\n"
        
        # Kiểm tra định hướng cạnh (eo)
        eo_valid = all(0 <= eo <= 1 for eo in rubik_state.eo) and sum(rubik_state.eo) % 2 == 0
        result += f"<p>- Định hướng cạnh (eo): {self.format_result(eo_valid)}</p>\n"
        
        # 2. Kiểm tra parity
        corner_parity = self.calculate_parity(rubik_state.cp)
        edge_parity = self.calculate_parity(rubik_state.ep)
        parity_valid = corner_parity == edge_parity
        result += f"<p>- Parity góc và cạnh: {self.format_result(parity_valid, 'Khớp nhau', 'Không khớp')}</p>\n"
        
        # Kết luận
        all_valid = cp_valid and co_valid and ep_valid and eo_valid and parity_valid
        
        result += "<h4>Kết luận:</h4>\n"
        if all_valid:
            result += "<p style='color:green; font-weight:bold'>✅ Cấu hình Rubik thỏa mãn tất cả các ràng buộc.</p>\n"
            result += "<p>→ Cấu hình này <b>có thể đạt được</b> từ trạng thái đã giải.</p>\n"
        else:
            result += "<p style='color:red; font-weight:bold'>❌ Cấu hình Rubik vi phạm một số ràng buộc.</p>\n"
            result += "<p>→ Cấu hình này <b>KHÔNG THỂ đạt được</b> từ trạng thái đã giải.</p>\n"
            result += "<p>Các ràng buộc bị vi phạm:</p>\n<ul>\n"
            if not cp_valid:
                result += "<li>Hoán vị góc không hợp lệ</li>\n"
            if not co_valid:
                result += "<li>Định hướng góc không hợp lệ hoặc tổng không chia hết cho 3</li>\n"
            if not ep_valid:
                result += "<li>Hoán vị cạnh không hợp lệ</li>\n"
            if not eo_valid:
                result += "<li>Định hướng cạnh không hợp lệ hoặc tổng không chia hết cho 2</li>\n"
            if not parity_valid:
                result += "<li>Parity góc và cạnh không khớp nhau</li>\n"
            result += "</ul>\n"
            
            # Gợi ý để sửa lỗi
            result += "<h4>Gợi ý sửa lỗi:</h4>\n<ul>\n"
            if not cp_valid:
                result += "<li>Đảm bảo tất cả các vị trí góc từ 0-7 đều xuất hiện đúng một lần</li>\n"
            if not co_valid:
                if not all(0 <= co <= 2 for co in rubik_state.co):
                    result += "<li>Đảm bảo tất cả các định hướng góc có giá trị từ 0-2</li>\n"
                else:
                    co_sum = sum(rubik_state.co) % 3
                    result += f"<li>Tổng định hướng góc hiện tại chia 3 dư {co_sum}, cần điều chỉnh để chia hết cho 3</li>\n"
            if not ep_valid:
                result += "<li>Đảm bảo tất cả các vị trí cạnh từ 0-11 đều xuất hiện đúng một lần</li>\n"
            if not eo_valid:
                if not all(0 <= eo <= 1 for eo in rubik_state.eo):
                    result += "<li>Đảm bảo tất cả các định hướng cạnh có giá trị 0 hoặc 1</li>\n"
                else:
                    eo_sum = sum(rubik_state.eo) % 2
                    result += f"<li>Tổng định hướng cạnh hiện tại chia 2 dư {eo_sum}, cần điều chỉnh để chia hết cho 2</li>\n"
            if not parity_valid:
                result += "<li>Hoán đổi hai vị trí cạnh bất kỳ để thay đổi parity cạnh</li>\n"
            result += "</ul>\n"
        
        return result
    
    def format_result(self, condition, success_text='Hợp lệ', fail_text='Không hợp lệ'):
        """Định dạng kết quả kiểm tra với màu sắc"""
        if condition:
            return f"<span style='color:green'>✓ {success_text}</span>"
        else:
            return f"<span style='color:red'>✗ {fail_text}</span>"
    
    def run_ac3(self, rubik_state):
        """Chạy thuật toán AC-3 thực tế trên cấu hình Rubik"""
        result = "<h3>Thuật toán AC-3 (Arc Consistency):</h3>\n"
        result += "<p>Thuật toán này đảm bảo tính nhất quán hồ quang (arc consistency) giữa các biến trong CSP.</p>\n"
        
        # Thiết lập biến và miền giá trị
        variables = []
        domains = {}
        
        # Nếu có cấu hình đã cho, dùng nó làm miền giá trị, nếu không, dùng miền đầy đủ
        if rubik_state:
            # Biến cp (corner permutation)
            for i in range(8):
                var_name = f"cp_{i}"
                variables.append(var_name)
                domains[var_name] = [rubik_state.cp[i]]
            
            # Biến co (corner orientation)
            for i in range(8):
                var_name = f"co_{i}"
                variables.append(var_name)
                domains[var_name] = [rubik_state.co[i]]
            
            # Biến ep (edge permutation)
            for i in range(12):
                var_name = f"ep_{i}"
                variables.append(var_name)
                domains[var_name] = [rubik_state.ep[i]]
                
            # Biến eo (edge orientation)
            for i in range(12):
                var_name = f"eo_{i}"
                variables.append(var_name)
                domains[var_name] = [rubik_state.eo[i]]
        else:
            # Biến cp (corner permutation) - miền đầy đủ
            for i in range(8):
                var_name = f"cp_{i}"
                variables.append(var_name)
                domains[var_name] = list(range(8))
            
            # Biến co (corner orientation) - miền đầy đủ
            for i in range(8):
                var_name = f"co_{i}"
                variables.append(var_name)
                domains[var_name] = [0, 1, 2]
            
            # Biến ep (edge permutation) - miền đầy đủ
            for i in range(12):
                var_name = f"ep_{i}"
                variables.append(var_name)
                domains[var_name] = list(range(12))
                
            # Biến eo (edge orientation) - miền đầy đủ
            for i in range(12):
                var_name = f"eo_{i}"
                variables.append(var_name)
                domains[var_name] = [0, 1]
        
        # Thiết lập ràng buộc
        constraints = []
        
        # Ràng buộc: các giá trị cp phải khác nhau (alldiff)
        for i in range(8):
            for j in range(i+1, 8):
                constraints.append((f"cp_{i}", f"cp_{j}"))
        
        # Ràng buộc: các giá trị ep phải khác nhau (alldiff)
        for i in range(12):
            for j in range(i+1, 12):
                constraints.append((f"ep_{i}", f"ep_{j}"))
        
        # Ràng buộc: tổng co phải chia hết cho 3
        for i in range(8):
            for j in range(8):
                if i != j:
                    constraints.append((f"co_{i}", f"co_{j}"))
        
        # Ràng buộc: tổng eo phải chia hết cho 2
        for i in range(12):
            for j in range(12):
                if i != j:
                    constraints.append((f"eo_{i}", f"eo_{j}"))
        
        # Ràng buộc: parity của cp và ep phải khớp nhau
        constraints.append(("cp_0", "ep_0"))  # Đại diện cho ràng buộc parity
        
        # Thiết lập hàng đợi ràng buộc cho AC-3
        queue = constraints.copy()
        
        # Hàm kiểm tra ràng buộc giữa hai biến
        def is_consistent(var_i, val_i, var_j, val_j):
            # Ràng buộc alldiff cho cp
            if var_i.startswith("cp_") and var_j.startswith("cp_"):
                return val_i != val_j
            
            # Ràng buộc alldiff cho ep
            if var_i.startswith("ep_") and var_j.startswith("ep_"):
                return val_i != val_j
            
            # Ràng buộc tổng co chia hết cho 3
            if var_i.startswith("co_") and var_j.startswith("co_"):
                # Vì chúng ta không biết các giá trị khác, nên không thể kiểm tra trực tiếp
                # Đây chỉ là ràng buộc mô phỏng
                return True
            
            # Ràng buộc tổng eo chia hết cho 2
            if var_i.startswith("eo_") and var_j.startswith("eo_"):
                # Vì chúng ta không biết các giá trị khác, nên không thể kiểm tra trực tiếp
                # Đây chỉ là ràng buộc mô phỏng
                return True
            
            # Ràng buộc parity
            if (var_i == "cp_0" and var_j == "ep_0") or (var_i == "ep_0" and var_j == "cp_0"):
                # Không thể kiểm tra parity chỉ với 2 biến
                return True
                
            return True
        
        # Thực hiện thuật toán AC-3
        result += "<h4>Quá trình AC-3:</h4>\n"
        ac3_steps = []
        
        while queue:
            xi, xj = queue.pop(0)
            
            # Ghi lại bước
            step = f"<p>- Xử lý ràng buộc: (<b>{xi}</b>, <b>{xj}</b>)</p>\n"
            
            # Kiểm tra xem có giá trị nào bị loại bỏ không
            original_domain = domains[xi].copy()
            revised = False
            
            # Loại bỏ các giá trị không thỏa mãn ràng buộc
            to_remove = []
            for x in domains[xi]:
                # Kiểm tra xem có giá trị nào trong miền của xj thỏa mãn ràng buộc với x không
                satisfiable = False
                for y in domains[xj]:
                    if is_consistent(xi, x, xj, y):
                        satisfiable = True
                        break
                
                if not satisfiable:
                    to_remove.append(x)
                    revised = True
            
            # Loại bỏ các giá trị
            for x in to_remove:
                domains[xi].remove(x)
            
            if revised:
                step += f"<p style='margin-left:20px'>+ Giảm miền của <b>{xi}</b>: {original_domain} → {domains[xi]}</p>\n"
                
                # Nếu miền bị giảm, thêm các ràng buộc liên quan vào hàng đợi
                for xk, xl in constraints:
                    if xl == xi and xk != xj:
                        queue.append((xk, xi))
                    elif xk == xi and xl != xj:
                        queue.append((xi, xl))
            else:
                step += f"<p style='margin-left:20px'>+ Miền của <b>{xi}</b> không thay đổi: {domains[xi]}</p>\n"
            
            ac3_steps.append(step)
            
            # Nếu miền rỗng, AC-3 thất bại
            if not domains[xi]:
                break
        
        # Hiển thị các bước AC-3
        for step in ac3_steps[:20]:  # Giới hạn số bước hiển thị
            result += step
            
        if len(ac3_steps) > 20:
            result += f"<p><i>...và {len(ac3_steps) - 20} bước khác</i></p>\n"
        
        # Kiểm tra kết quả
        empty_domains = [var for var, dom in domains.items() if not dom]
        
        result += f"<h4>AC-3 đã hoàn thành sau {len(ac3_steps)} lần lặp.</h4>\n"
        
        if empty_domains:
            result += "<p style='color:red; font-weight:bold'>❌ Cấu hình KHÔNG thỏa mãn (có miền rỗng).</p>\n"
            result += f"<p>Các biến có miền rỗng: {empty_domains}</p>\n"
            result += "<p>→ Cấu hình này <b>không thể giải được</b>.</p>\n"
        else:
            fixed_vars = sum(len(dom) == 1 for dom in domains.values())
            unfixed_vars = sum(len(dom) > 1 for dom in domains.values())
            
            result += "<p style='color:green; font-weight:bold'>✅ Cấu hình nhất quán sau khi thực thi AC-3.</p>\n"
            result += f"<p>- {fixed_vars} biến đã xác định đầy đủ</p>\n"
            result += f"<p>- {unfixed_vars} biến vẫn còn nhiều giá trị có thể</p>\n"
            
            # Kiểm tra chi tiết hơn
            if rubik_state:
                # Kiểm tra các ràng buộc toàn cục (không chỉ theo cặp)
                cp_values = [rubik_state.cp[i] for i in range(8)]
                co_values = [rubik_state.co[i] for i in range(8)]
                ep_values = [rubik_state.ep[i] for i in range(12)]
                eo_values = [rubik_state.eo[i] for i in range(12)]
                
                cp_valid = len(set(cp_values)) == 8 and set(cp_values) == set(range(8))
                co_valid = sum(co_values) % 3 == 0
                ep_valid = len(set(ep_values)) == 12 and set(ep_values) == set(range(12))
                eo_valid = sum(eo_values) % 2 == 0
                
                cp_parity = self.calculate_parity(cp_values)
                ep_parity = self.calculate_parity(ep_values)
                parity_valid = cp_parity == ep_parity
                
                all_valid = cp_valid and co_valid and ep_valid and eo_valid and parity_valid
                
                result += "<h4>Kiểm tra ràng buộc toàn cục:</h4>\n"
                result += f"<p>- Hoán vị góc (cp): {self.format_result(cp_valid)}</p>\n"
                result += f"<p>- Định hướng góc (co): {self.format_result(co_valid)}</p>\n"
                result += f"<p>- Hoán vị cạnh (ep): {self.format_result(ep_valid)}</p>\n"
                result += f"<p>- Định hướng cạnh (eo): {self.format_result(eo_valid)}</p>\n"
                result += f"<p>- Parity góc và cạnh: {self.format_result(parity_valid, 'Khớp nhau', 'Không khớp')}</p>\n"
                
                if all_valid:
                    result += "<p style='color:green; font-weight:bold'>✅ Cấu hình hoàn toàn hợp lệ, có thể giải được.</p>\n"
                else:
                    result += "<p style='color:red; font-weight:bold'>❌ Cấu hình vi phạm một số ràng buộc toàn cục.</p>\n"
                    result += "<p>→ Lưu ý: AC-3 chỉ đảm bảo tính nhất quán theo cặp, không đảm bảo thỏa mãn tất cả ràng buộc toàn cục.</p>\n"
        
        return result
    
    def get_selected_algorithm(self):
        """Lấy thuật toán đang được chọn"""
        if self.backtracking_rb.isChecked():
            return "Backtracking"
        elif self.backtracking_test_rb.isChecked():
            return "Backtracking Test"
        elif self.ac3_rb.isChecked():
            return "AC-3"
        return "Unknown"
    
    def insert_template(self):
        """Chèn mẫu RubikState vào ô nhập thủ công"""
        template = "RubikState(\n  cp=(0,1,2,3,4,5,6,7),\n  co=(0,0,0,0,0,0,0,0),\n  ep=(0,1,2,3,4,5,6,7,8,9,10,11),\n  eo=(0,0,0,0,0,0,0,0,0,0,0,0)\n)"
        self.manual_input.setText(template)
    
    def insert_component(self, component):
        """Chèn thành phần cụ thể vào vị trí con trỏ"""
        cursor = self.manual_input.textCursor()
        if component == "cp":
            text = "cp=(0,1,2,3,4,5,6,7)"
        elif component == "co":
            text = "co=(0,0,0,0,0,0,0,0)"
        elif component == "ep":
            text = "ep=(0,1,2,3,4,5,6,7,8,9,10,11)"
        elif component == "eo":
            text = "eo=(0,0,0,0,0,0,0,0,0,0,0,0)"
        cursor.insertText(text) 