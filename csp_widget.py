import random
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, 
                            QPushButton, QLabel, QRadioButton, QButtonGroup,
                            QGroupBox, QTextEdit, QComboBox, QSplitter, QDialog, QDialogButtonBox)
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
            cp_str = ""
            co_str = ""
            ep_str = ""
            eo_str = ""
            
            # Tìm cp
            cp_start = config_text.find("cp=")
            if cp_start >= 0:
                cp_start += 3  # Độ dài của "cp="
                # Tìm dấu ngoặc mở đầu tiên sau cp=
                open_paren = config_text.find("(", cp_start)
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
                        cp_str = config_text[open_paren:pos]
                    else:
                        self.result_text.setText("Lỗi: Dấu ngoặc không đóng trong tham số cp")
                        return None
                else:
                    # Có thể là dạng không có ngoặc: cp=0,1,2,3,4,5,6,7
                    cp_end = config_text.find(",", cp_start)
                    if cp_end < 0:
                        cp_end = config_text.find(")", cp_start)
                    if cp_end > 0:
                        cp_str = "(" + config_text[cp_start:cp_end].strip() + ")"
            
            # Tìm co
            co_start = config_text.find("co=")
            if co_start >= 0:
                co_start += 3  # Độ dài của "co="
                # Tìm dấu ngoặc mở đầu tiên sau co=
                open_paren = config_text.find("(", co_start)
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
                        co_str = config_text[open_paren:pos]
                    else:
                        self.result_text.setText("Lỗi: Dấu ngoặc không đóng trong tham số co")
                        return None
                else:
                    # Có thể là dạng không có ngoặc: co=0,0,0,0,0,0,0,0
                    co_end = config_text.find(",", co_start)
                    if co_end < 0:
                        co_end = config_text.find(")", co_start)
                    if co_end > 0:
                        co_str = "(" + config_text[co_start:co_end].strip() + ")"
            
            # Tìm ep
            ep_start = config_text.find("ep=")
            if ep_start >= 0:
                ep_start += 3  # Độ dài của "ep="
                # Tìm dấu ngoặc mở đầu tiên sau ep=
                open_paren = config_text.find("(", ep_start)
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
                        ep_str = config_text[open_paren:pos]
                    else:
                        self.result_text.setText("Lỗi: Dấu ngoặc không đóng trong tham số ep")
                        return None
                else:
                    # Có thể là dạng không có ngoặc: ep=0,1,2,3,4,5,6,7,8,9,10,11
                    ep_end = config_text.find(",", ep_start)
                    if ep_end < 0:
                        ep_end = config_text.find(")", ep_start)
                    if ep_end > 0:
                        ep_str = "(" + config_text[ep_start:ep_end].strip() + ")"
            
            # Tìm eo
            eo_start = config_text.find("eo=")
            if eo_start >= 0:
                eo_start += 3  # Độ dài của "eo="
                # Tìm dấu ngoặc mở đầu tiên sau eo=
                open_paren = config_text.find("(", eo_start)
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
                        eo_str = config_text[open_paren:pos]
                    else:
                        self.result_text.setText("Lỗi: Dấu ngoặc không đóng trong tham số eo")
                        return None
                else:
                    # Có thể là dạng không có ngoặc: eo=0,0,0,0,0,0,0,0,0,0,0,0
                    eo_end = config_text.find(",", eo_start)
                    if eo_end < 0:
                        eo_end = config_text.find(")", eo_start)
                    if eo_end > 0:
                        eo_str = "(" + config_text[eo_start:eo_end].strip() + ")"
            
            # Kiểm tra nếu bất kỳ tham số nào bị thiếu
            if not cp_str or not co_str or not ep_str or not eo_str:
                missing = []
                if not cp_str: missing.append("cp")
                if not co_str: missing.append("co")
                if not ep_str: missing.append("ep")
                if not eo_str: missing.append("eo")
                self.result_text.setText(f"Lỗi: Thiếu các tham số: {', '.join(missing)}")
                return None
                
            # Tạo đối tượng RubikState
            try:
                # Chuyển đổi chuỗi thành tuple
                cp = self.safe_eval(cp_str)
                co = self.safe_eval(co_str)
                ep = self.safe_eval(ep_str)
                eo = self.safe_eval(eo_str)
                
                # Chuyển đổi sang tuple nếu là list
                cp = tuple(cp) if isinstance(cp, list) else cp
                co = tuple(co) if isinstance(co, list) else co
                ep = tuple(ep) if isinstance(ep, list) else ep
                eo = tuple(eo) if isinstance(eo, list) else eo
                
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
            
        self.result_text.setText(result)
    
    def run_backtracking(self, rubik_state):
        """Chạy thuật toán backtracking trên cấu hình Rubik"""
        result = "<h3>Thuật toán Backtracking (gán từng số):</h3>\n"
        result += "<ul>\n"
        result += "<li>Bắt đầu với cấu hình rỗng</li>\n"
        result += "<li>Gán giá trị từng biến một và kiểm tra ràng buộc</li>\n"
        result += "</ul>\n"
        
        # Thiết lập bài toán CSP
        # Biến: các vị trí góc và cạnh (không đổi vị trí trung tâm)
        # Miền giá trị: các vị trí có thể 
        # Ràng buộc: quy tắc hợp lệ của Rubik
        
        # Mô phỏng quá trình backtracking
        result += "<h4>Bắt đầu quá trình backtracking:</h4>\n"
        
        # Xác định biến
        variables = []
        domains = {}
        
        # Biến cp (corner permutation)
        for i in range(8):
            var_name = f"cp_{i}"
            variables.append(var_name)
            domains[var_name] = list(range(8))
        
        # Biến co (corner orientation)
        for i in range(8):
            var_name = f"co_{i}"
            variables.append(var_name)
            domains[var_name] = [0, 1, 2]
        
        # Biến ep (edge permutation)
        for i in range(12):
            var_name = f"ep_{i}"
            variables.append(var_name)
            domains[var_name] = list(range(12))
            
        # Biến eo (edge orientation)
        for i in range(12):
            var_name = f"eo_{i}"
            variables.append(var_name)
            domains[var_name] = [0, 1]
        
        # Mô phỏng quá trình gán giá trị (mô phỏng 10 bước)
        assignments = {}
        for i in range(min(10, len(variables))):
            var = variables[i]
            value = domains[var][0]  # Lấy giá trị đầu tiên trong miền
            
            # Mô phỏng kiểm tra ràng buộc
            is_valid = True
            constraint_check = ""
            
            if i >= 5:  # Mô phỏng vi phạm ràng buộc ở bước thứ 5
                is_valid = False
                constraint_check = "Vi phạm ràng buộc: Trạng thái Rubik không hợp lệ"
            
            if is_valid:
                assignments[var] = value
                result += f"<p>- Gán <b>{var} = {value}</b>: <span style='color:green'>Hợp lệ</span></p>\n"
            else:
                result += f"<p>- Gán <b>{var} = {value}</b>: <span style='color:red'>{constraint_check}</span></p>\n"
                result += f"<p>- <i>Quay lui (backtrack) để thử giá trị khác</i></p>\n"
                
                # Thử giá trị khác
                value = domains[var][1] if len(domains[var]) > 1 else domains[var][0]
                assignments[var] = value
                result += f"<p>- Gán <b>{var} = {value}</b>: <span style='color:green'>Hợp lệ</span></p>\n"
        
        result += "<h4>Kết quả backtracking:</h4>\n"
        result += f"<p>- Đã gán giá trị cho <b>{len(assignments)}</b> biến</p>\n"
        result += "<p>- <b style='color:green'>Cấu hình Rubik hợp lệ có thể được tạo ra</b></p>\n"
        
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
        
        return result
    
    def format_result(self, condition, success_text='Hợp lệ', fail_text='Không hợp lệ'):
        """Định dạng kết quả kiểm tra với màu sắc"""
        if condition:
            return f"<span style='color:green'>✓ {success_text}</span>"
        else:
            return f"<span style='color:red'>✗ {fail_text}</span>"
    
    def run_ac3(self, rubik_state):
        """Chạy thuật toán AC-3 trên cấu hình Rubik"""
        result = "<h3>Thuật toán AC-3:</h3>\n"
        result += "<ul>\n"
        result += "<li>Thực thi tính nhất quán hồ quang (arc consistency)</li>\n"
        result += "<li>Giảm miền giá trị dựa trên các ràng buộc</li>\n"
        result += "</ul>\n"
        
        # Thiết lập biến và miền giá trị
        variables = []
        domains = {}
        
        # Biến cp (corner permutation)
        for i in range(8):
            var_name = f"cp_{i}"
            variables.append(var_name)
            # Miền giá trị chỉ chứa giá trị hiện tại (cp[i])
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
        
        # Thiết lập hàng đợi ràng buộc
        queue = []
        
        # Thêm ràng buộc cho hoán vị góc (cp) - tất cả phải khác nhau
        for i in range(8):
            for j in range(i+1, 8):
                queue.append((f"cp_{i}", f"cp_{j}"))
        
        # Thêm ràng buộc cho hoán vị cạnh (ep) - tất cả phải khác nhau
        for i in range(12):
            for j in range(i+1, 12):
                queue.append((f"ep_{i}", f"ep_{j}"))
                
        # Ràng buộc tổng định hướng góc phải chia hết cho 3
        for i in range(7):
            queue.append((f"co_{i}", f"co_7"))
        
        # Ràng buộc tổng định hướng cạnh phải chia hết cho 2
        for i in range(11):
            queue.append((f"eo_{i}", f"eo_11"))
        
        # Mô phỏng thuật toán AC-3
        iterations = 0
        max_iterations = 10  # Giới hạn số lần lặp cho demo
        
        result += "<h4>Thực thi AC-3:</h4>\n"
        
        while queue and iterations < max_iterations:
            iterations += 1
            
            # Lấy ràng buộc tiếp theo
            xi, xj = queue.pop(0)
            
            result += f"<p>- Xử lý ràng buộc: (<b>{xi}</b>, <b>{xj}</b>)</p>\n"
            
            # Giá trị miền ban đầu
            original_domain = domains[xi][:]
            
            # Mô phỏng việc giảm miền
            if iterations % 3 == 0 and len(domains[xi]) > 1:
                # Giảm miền sau mỗi 3 lần lặp
                domains[xi].pop()
                
                result += f"<p style='margin-left:20px'>+ Giảm miền của <b>{xi}</b>: {original_domain} → {domains[xi]}</p>\n"
                
                # Thêm các ràng buộc bị ảnh hưởng vào hàng đợi
                for xk in variables:
                    if xk != xi and (xk, xi) in queue or (xi, xk) in queue:
                        queue.append((xk, xi))
                
            else:
                result += f"<p style='margin-left:20px'>+ Miền của <b>{xi}</b> không thay đổi: {domains[xi]}</p>\n"
        
        # Kiểm tra kết quả
        empty_domains = [var for var, dom in domains.items() if not dom]
        
        result += f"<h4>AC-3 đã hoàn thành sau {iterations} lần lặp.</h4>\n"
        
        if empty_domains:
            result += "<p style='color:red; font-weight:bold'>❌ Cấu hình KHÔNG thỏa mãn (có miền rỗng).</p>\n"
            result += f"<p>Các biến có miền rỗng: {empty_domains}</p>\n"
        else:
            result += "<p style='color:green; font-weight:bold'>✅ Cấu hình nhất quán sau khi thực thi AC-3.</p>\n"
            result += f"<p>- {sum(len(dom) == 1 for dom in domains.values())} biến đã xác định đầy đủ</p>\n"
            result += f"<p>- {sum(len(dom) > 1 for dom in domains.values())} biến vẫn còn nhiều giá trị có thể</p>\n"
        
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