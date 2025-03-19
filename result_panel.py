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
        left_layout.addWidget(self.algo_label)
        
        # Label cho loading animation
        self.loading_label = QLabel()
        self.loading_label.hide()
        left_layout.addWidget(self.loading_label)
        
        # Text area để hiển thị kết quả
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        left_layout.addWidget(self.result_text)
        
        # Add performance metrics display
        self.metrics_group = QGroupBox("Performance Metrics")
        metrics_layout = QVBoxLayout()
        self.metrics_text = QTextEdit()
        self.metrics_text.setReadOnly(True)
        self.metrics_text.setMaximumHeight(100)
        self.metrics_text.setStyleSheet("font-family: monospace; font-size: 9pt;")
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
        self.info_text.setStyleSheet("background-color: #f5f5f5;")
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
        solution_layout.addWidget(self.current_step_label)
        
        # Current move display
        self.current_move_label = QLabel("Current move: None")
        solution_layout.addWidget(self.current_move_label)
        
        # Button controls
        buttons_layout = QHBoxLayout()
        
        self.next_step_btn = QPushButton("Next Step")
        self.next_step_btn.setEnabled(False)
        self.next_step_btn.clicked.connect(self.execute_next_step)
        
        self.execute_all_btn = QPushButton("Execute All")
        self.execute_all_btn.setEnabled(False)
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
        
        # Set reasonable sizes (ratio 2:1:1)
        splitter.setSizes([400, 200, 200])
        
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
        self.loading_label.setText("Solving" + "." * self.animation_dots)
        
    def set_algorithm(self, name):
        """Set tên thuật toán đang chạy"""
        self.algo_label.setText(f"Running: {name}")
        self.loading_label.show()
        self.animation_timer.start(500)  # Cập nhật mỗi 500ms
        
        # Clear the info text
        self.info_text.clear()
        
    def clear_results(self):
        """Xóa kết quả"""
        self.result_text.clear()
        self.info_text.clear()
        self.loading_label.show()
        self.animation_dots = 0
        self.animation_timer.start(500)
        
        # Reset solution and buttons state
        self.current_solution = []
        self.current_step = 0
        self.next_step_btn.setEnabled(False)
        self.execute_all_btn.setEnabled(False)
        self.current_step_label.setText("Steps: 0/0")
        self.current_move_label.setText("Current move: None")
        
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
            
        # Format the metrics for display
        text = f"Runtime: {metrics.get('runtime_seconds', 0):.2f}s\n"
        text += f"Tasks: {metrics.get('tasks_completed', 0)}/{metrics.get('tasks_submitted', 0)}\n"
        text += f"Rate: {metrics.get('tasks_per_second', 0):.2f} tasks/sec\n"
        
        # Add detailed counters if available
        counters = metrics.get('counters', {})
        if counters:
            text += "\nBreakdown:\n"
            for key, value in counters.items():
                if isinstance(value, (int, float)):
                    text += f"- {key}: {value:.2f}\n"
            
        self.metrics_text.setText(text)
        self.metrics_group.show()
        
    def set_rubik_widget(self, widget):
        """Set reference to rubik widget"""
        self.rubik_widget = widget
        
    def execute_next_step(self):
        """Thực hiện bước tiếp theo trong solution"""
        if not self.rubik_widget or not self.current_solution or self.current_step >= len(self.current_solution):
            return
            
        move = self.current_solution[self.current_step]
        
        # Parse the move
        face = move[0]
        clockwise = True
        if len(move) > 1 and move[1] == "'":
            clockwise = False
            
        # Apply the move - check if animation is in progress
        if not self.rubik_widget.rubik.animating:
            self.rubik_widget.rubik.rotate_face(face, clockwise)
            
            # Update step counter
            self.current_step += 1
            self.current_step_label.setText(f"Steps: {self.current_step}/{len(self.current_solution)}")
            self.current_move_label.setText(f"Current move: {move}")
            
            # Disable button if we're at the end
            if self.current_step >= len(self.current_solution):
                self.next_step_btn.setEnabled(False)
                self.execute_all_btn.setEnabled(False)
        
    def execute_all_steps(self):
        """Thực hiện tất cả các bước còn lại"""
        if not self.rubik_widget or not self.current_solution:
            return
            
        # Queue all remaining moves to the rubik widget
        remaining_moves = []
        for i in range(self.current_step, len(self.current_solution)):
            move = self.current_solution[i]
            face = move[0]
            clockwise = True
            if len(move) > 1 and move[1] == "'":
                clockwise = False
            remaining_moves.append((face, clockwise))
            
        # Add first move directly and rest to queue if animation is not active
        if remaining_moves and not self.rubik_widget.rubik.animating:
            first_move = remaining_moves.pop(0)
            self.rubik_widget.rubik.rotate_face(first_move[0], first_move[1])
            self.rubik_widget.move_queue.extend(remaining_moves)
            
            # Update UI
            self.current_step = len(self.current_solution)
            self.current_step_label.setText(f"Steps: {self.current_step}/{len(self.current_solution)}")
            
            # Disable buttons
            self.next_step_btn.setEnabled(False)
            self.execute_all_btn.setEnabled(False)
