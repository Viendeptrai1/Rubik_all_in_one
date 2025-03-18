import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from rubik_widget import RubikWidget
from controls_widget import ControlsWidget
from result_panel import ResultPanel

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Rubik Solver')
        self.resize(1600, 900)

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
        
        # Set kích thước cố định cho dock
        dock.setFixedWidth(300)
        
        # Kết nối ResultPanel với ControlsWidget
        self.controls.set_result_panel(self.result_panel)

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()