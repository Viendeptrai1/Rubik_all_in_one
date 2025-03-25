import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from rubik_widget import RubikWidget
from controls_widget import ControlsWidget
from result_panel import ResultPanel
from thread_manager import thread_manager  # Import thread manager early
from rubik_state import RubikState, SOLVED_STATE  # Import RubikState mới
import rubik_converter  # Import module chuyển đổi

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Rubik Solver')
        self.resize(1800, 900)  # Tăng kích thước mặc định của cửa sổ

        # Widget chính chứa layout
        central_widget = QWidget()
        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        # Tạo splitter dọc cho khu vực bên trái
        left_splitter = QSplitter(Qt.Vertical)
        
        # Widget trung tâm để render Rubik
        self.rubik_widget = RubikWidget()
        left_splitter.addWidget(self.rubik_widget)
        
        # Thêm panel kết quả
        self.result_panel = ResultPanel()
        left_splitter.addWidget(self.result_panel)
        
        # Set tỷ lệ khởi tạo cho splitter (70% Rubik, 30% Result)
        left_splitter.setSizes([700, 300])
        
        # Thêm splitter vào layout chính
        main_layout.addWidget(left_splitter)

        # Dock widget bên phải cho controls
        dock = QDockWidget("Controls", self)
        dock.setFeatures(QDockWidget.NoDockWidgetFeatures)
        self.controls = ControlsWidget(self.rubik_widget)
        dock.setWidget(self.controls)
        self.addDockWidget(Qt.RightDockWidgetArea, dock)
        
        # Tăng kích thước cố định cho dock
        dock.setFixedWidth(400)  # Tăng chiều rộng từ 300 lên 400
        
        # Kết nối ResultPanel với ControlsWidget
        self.controls.set_result_panel(self.result_panel)
        
        # Thêm biến lưu trữ trạng thái Rubik dạng hoán vị và định hướng
        self.rubik_state = SOLVED_STATE.copy()
        
        # Kết nối sự kiện cập nhật trạng thái giữa biểu diễn 3D và biểu diễn hoán vị/định hướng
        self.rubik_widget.cube_updated.connect(self.update_rubik_state)

    def update_rubik_state(self):
        """Cập nhật trạng thái Rubik khi biểu diễn 3D thay đổi"""
        try:
            # Chuyển đổi từ biểu diễn 3D sang biểu diễn hoán vị/định hướng
            self.rubik_state = rubik_converter.cube_to_state(self.rubik_widget.cube)
            # Debug: In ra trạng thái hoán vị và định hướng
            print("Updated RubikState:")
            print(f"Corner Permutation: {self.rubik_state.cp}")
            print(f"Corner Orientation: {self.rubik_state.co}")
            print(f"Edge Permutation: {self.rubik_state.ep}")
            print(f"Edge Orientation: {self.rubik_state.eo}")
        except Exception as e:
            print(f"Error updating RubikState: {str(e)}")

    def get_current_state(self):
        """Trả về trạng thái Rubik hiện tại dưới dạng RubikState"""
        return self.rubik_state

def main():
    app = QApplication(sys.argv)
    
    # Initialize thread pool early and show core allocation
    print(f"Starting with {thread_manager.NUM_CORES} computation cores and {thread_manager.UI_CORES} UI cores")
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()