from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

class ResultPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Layout chính
        main_layout = QHBoxLayout()
        
        # ===== Phần trái - Kết quả =====
        left_panel = QWidget()
        left_layout = QVBoxLayout()
        
        # Label hiển thị tên thuật toán đang chạy
        self.algo_label = QLabel("No algorithm running")
        # Tăng kích thước font
        font = self.algo_label.font()
        font.setPointSize(12)
        font.setBold(True)
        self.algo_label.setFont(font)
        self.algo_label.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(self.algo_label)
        
        # Label cho loading animation
        self.loading_label = QLabel()
        # Tăng kích thước font
        font = self.loading_label.font()
        font.setPointSize(11)
        self.loading_label.setFont(font)
        self.loading_label.setAlignment(Qt.AlignCenter)
        self.loading_label.hide()
        left_layout.addWidget(self.loading_label)
        
        # Text area để hiển thị kết quả
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        # Tăng kích thước font
        font = self.result_text.font()
        font.setPointSize(11)
        self.result_text.setFont(font)
        left_layout.addWidget(self.result_text)
        
        # Add performance metrics display
        self.metrics_group = QGroupBox("Performance Metrics")
        metrics_layout = QVBoxLayout()
        self.metrics_text = QTextEdit()
        self.metrics_text.setReadOnly(True)
        self.metrics_text.setMaximumHeight(120)  # Tăng chiều cao từ 100 lên 120
        self.metrics_text.setStyleSheet("font-family: monospace; font-size: 10pt;")  # Tăng cỡ chữ từ 9pt lên 10pt
        metrics_layout.addWidget(self.metrics_text)
        self.metrics_group.setLayout(metrics_layout)
        self.metrics_group.hide()
        left_layout.addWidget(self.metrics_group)
        
        # Add progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("%v/%m (%p%)")
        self.progress_bar.setMinimumHeight(20)  # Đảm bảo progress bar đủ cao
        self.progress_bar.hide()
        left_layout.addWidget(self.progress_bar)
        
        left_panel.setLayout(left_layout)
        
        # ===== Phần giữa - Thông tin thuật toán =====
        middle_panel = QWidget()
        middle_layout = QVBoxLayout()
        
        # Algorithm info box
        info_group = QGroupBox("Algorithm Information")
        info_box_layout = QVBoxLayout()
        
        # Text area for algorithm info
        self.info_text = QTextEdit()
        self.info_text.setReadOnly(True)
        self.info_text.setStyleSheet("background-color: #f5f5f5; font-size: 11pt;")  # Tăng cỡ chữ
        info_box_layout.addWidget(self.info_text)
        
        info_group.setLayout(info_box_layout)
        middle_layout.addWidget(info_group)
        
        middle_panel.setLayout(middle_layout)
        
        # ===== Phần phải - Điều khiển giải pháp =====
        right_panel = QWidget()
        right_layout = QVBoxLayout()
        
        solution_group = QGroupBox("Solution Execution")
        solution_layout = QVBoxLayout()
        
        # Hiển thị bước hiện tại
        self.current_step_label = QLabel("Steps: 0/0")
        # Tăng kích thước font
        font = self.current_step_label.font()
        font.setPointSize(11)
        self.current_step_label.setFont(font)
        solution_layout.addWidget(self.current_step_label)
        
        # Current move display
        self.current_move_label = QLabel("Current move: None")
        # Tăng kích thước font
        font = self.current_move_label.font()
        font.setPointSize(11)
        self.current_move_label.setFont(font)
        solution_layout.addWidget(self.current_move_label)
        
        # Button controls
        buttons_layout = QHBoxLayout()
        
        self.next_step_btn = QPushButton("Next Step")
        self.next_step_btn.setEnabled(False)
        # Tăng kích thước font và chiều cao
        font = self.next_step_btn.font()
        font.setPointSize(11)
        self.next_step_btn.setFont(font)
        self.next_step_btn.setMinimumHeight(36)
        self.next_step_btn.clicked.connect(self.execute_next_step)
        
        self.execute_all_btn = QPushButton("Execute All")
        self.execute_all_btn.setEnabled(False)
        # Tăng kích thước font và chiều cao
        font = self.execute_all_btn.font()
        font.setPointSize(11)
        self.execute_all_btn.setFont(font)
        self.execute_all_btn.setMinimumHeight(36)
        self.execute_all_btn.clicked.connect(self.execute_all_steps)
        
        buttons_layout.addWidget(self.next_step_btn)
        buttons_layout.addWidget(self.execute_all_btn)
        
        solution_layout.addLayout(buttons_layout)
        solution_group.setLayout(solution_layout)
        
        right_layout.addWidget(solution_group)
        right_layout.addStretch()  # Add stretch to push controls to the top
        
        right_panel.setLayout(right_layout)
        
        # Create a splitter to hold all panels
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(left_panel)
        splitter.addWidget(middle_panel)
        splitter.addWidget(right_panel)
        
        # Set reasonable sizes (ratio 4:3:3)
        splitter.setSizes([400, 300, 300])
        
        main_layout.addWidget(splitter)
        self.setLayout(main_layout)
        
        # Timer cho animation
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self._update_animation)
        self.animation_dots = 0
        
        # Lưu solution hiện tại
        self.current_solution = []
        self.current_step = 0
        self.rubik_widget = None  # Sẽ được set từ bên ngoài
    
    def _update_animation(self):
        """Cập nhật animation loading"""
        self.animation_dots = (self.animation_dots + 1) % 4
        dots = "." * self.animation_dots
        while len(dots) < 3:  # Đảm bảo đủ 3 ký tự để animation không làm thay đổi kích thước
            dots += " "
        self.loading_label.setText(f"Processing{dots}")
        
    def set_algorithm(self, algo_name):
        """Cập nhật tên thuật toán đang chạy và hiển thị animation loading"""
        if not algo_name:
            self.algo_label.setText("")
            self._stop_animation()
            return
        
        # Hiển thị tên thuật toán thay vì "Running"
        self.algo_label.setText(f"{algo_name}")
        self._start_animation()
        
        # Clear the info text
        self.info_text.clear()
        
        # Reset progress bar
        self.progress_bar.setValue(0)
        self.progress_bar.show()
        
    def _start_animation(self):
        """Start animation"""
        self.loading_label.show()
        self.animation_timer.start(500)  # Cập nhật mỗi 500ms
        
    def _stop_animation(self):
        """Stop animation"""
        self.loading_label.hide()
        self.animation_timer.stop()
        
    def clear_results(self):
        """Xóa kết quả"""
        self.result_text.clear()
        self.info_text.clear()
        
        # Reset solution and buttons state
        self.current_solution = []
        self.current_step = 0
        self.next_step_btn.setEnabled(False)
        self.execute_all_btn.setEnabled(False)
        self.current_step_label.setText("Steps: 0/0")
        self.current_move_label.setText("Current move: None")
        
        # Hide progress bar
        self.progress_bar.setValue(0)
        self.progress_bar.hide()
        
        # Hide and clear metrics
        self.metrics_group.hide()
        self.metrics_text.clear()
        
    def add_result(self, text):
        """Thêm text vào kết quả"""
        self.result_text.append(text)
        
    def set_progress(self, current, total):
        """Cập nhật giá trị progress bar"""
        if total > 0:
            self.progress_bar.setRange(0, total)
            self.progress_bar.setValue(current)
            self.progress_bar.show()
        else:
            self.progress_bar.hide()
        
    def update_results(self, solution, time, complexity):
        """Cập nhật kết quả giải"""
        self.animation_timer.stop()
        self.loading_label.hide()
        self.result_text.setText(f"Solution: {solution}\n")
        self.result_text.append(f"Time: {time:.3f}s\n")
        self.result_text.append(f"Complexity: {complexity}")
        
        # Lưu solution và reset step counter
        if isinstance(solution, str):
            self.current_solution = solution.split()
        else:
            self.current_solution = solution
            
        self.current_step = 0
        
        # Cập nhật các controls
        if self.current_solution:
            self.current_step_label.setText(f"Steps: 0/{len(self.current_solution)}")
            self.current_move_label.setText(f"Current move: None")
            self.next_step_btn.setEnabled(True)
            self.execute_all_btn.setEnabled(True)
        
    def update_info(self, info):
        """Cập nhật thông tin thuật toán"""
        self.info_text.setText(info)
        
    def update_metrics(self, metrics):
        """Update performance metrics display"""
        if not metrics:
            self.metrics_group.hide()
            return
            
        self.metrics_group.show()
        
        # Format metrics nicely
        text = ""
        if "runtime_seconds" in metrics:
            text += f"Runtime: {metrics['runtime_seconds']:.2f}s\n"
        
        if "tasks_completed" in metrics and "tasks_submitted" in metrics:
            text += f"Tasks: {metrics['tasks_completed']}/{metrics['tasks_submitted']}"
            
            if "tasks_per_second" in metrics:
                text += f" ({metrics['tasks_per_second']:.2f}/s)\n"
            else:
                text += "\n"
        
        if "counters" in metrics:
            counters = metrics["counters"]
            if counters:
                text += "\nPerformance Counters:\n"
                for name, value in counters.items():
                    text += f"  {name}: {value}\n"
        
        self.metrics_text.setText(text)
    
    def set_rubik_widget(self, widget):
        """Set reference to RubikWidget"""
        self.rubik_widget = widget
    
    def execute_next_step(self):
        """Execute the next step in solution"""
        if not self.current_solution or self.current_step >= len(self.current_solution):
            return
            
        # Get the move to execute
        move = self.current_solution[self.current_step]
        self.current_step += 1
        
        # Update the UI
        self.current_step_label.setText(f"Steps: {self.current_step}/{len(self.current_solution)}")
        self.current_move_label.setText(f"Current move: {move}")
        
        # Determine the parameters for the move
        if self.rubik_widget:
            # Parse the move string
            face = move[0]  # First character is the face (U, D, R, L, F, B)
            clockwise = True
            
            if len(move) > 1:
                if move[1] == "'":
                    clockwise = False
                elif move[1] == "2":
                    # Double move - we'll execute it as two moves for now
                    face = move[0]
                    self.rubik_widget.rotate_face(face, clockwise)
                    self.rubik_widget.rotate_face(face, clockwise)
                    return
            
            # Execute the move
            self.rubik_widget.rotate_face(face, clockwise)
            
            # Disable buttons if we've reached the end
            if self.current_step >= len(self.current_solution):
                self.next_step_btn.setEnabled(False)
                self.execute_all_btn.setEnabled(False)
    
    def execute_all_steps(self):
        """Execute all remaining steps in solution"""
        while self.current_step < len(self.current_solution) and self.rubik_widget:
            self.execute_next_step()
