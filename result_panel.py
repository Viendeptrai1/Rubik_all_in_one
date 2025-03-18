from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

class ResultPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Layout chính
        layout = QVBoxLayout()
        
        # Label hiển thị tên thuật toán đang chạy
        self.algo_label = QLabel("No algorithm running")
        layout.addWidget(self.algo_label)
        
        # Text area để hiển thị kết quả
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        layout.addWidget(self.result_text)
        
        # Progress bar
        self.progress = QProgressBar()
        self.progress.hide()
        layout.addWidget(self.progress)
        
        self.setLayout(layout)
    
    def set_algorithm(self, name):
        """Set tên thuật toán đang chạy"""
        self.algo_label.setText(f"Running: {name}")
        
    def clear_results(self):
        """Xóa kết quả"""
        self.result_text.clear()
        self.progress.hide()
        
    def add_result(self, text):
        """Thêm text vào kết quả"""
        self.result_text.append(text)
        
    def set_progress(self, value):
        """Cập nhật progress bar"""
        self.progress.show()
        self.progress.setValue(value)
