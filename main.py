import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from rubik_widget import RubikWidget, RubikWidget2x2
from controls_widget import ControlsWidget

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Rubik Cube')
        self.resize(1200, 800)

        # Widget chính chứa layout
        central_widget = QWidget()
        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        # Tạo tab widget để chuyển đổi giữa Rubik 3x3 và 2x2
        tabs = QTabWidget()
        
        # Tab cho Rubik 3x3
        tab_3x3 = QWidget()
        layout_3x3 = QVBoxLayout()
        self.rubik_widget_3x3 = RubikWidget()
        layout_3x3.addWidget(self.rubik_widget_3x3)
        tab_3x3.setLayout(layout_3x3)
        
        # Tab cho Rubik 2x2
        tab_2x2 = QWidget()
        layout_2x2 = QVBoxLayout()
        self.rubik_widget_2x2 = RubikWidget2x2()
        layout_2x2.addWidget(self.rubik_widget_2x2)
        tab_2x2.setLayout(layout_2x2)
        
        # Thêm các tab vào tab widget
        tabs.addTab(tab_3x3, "Rubik 3x3")
        tabs.addTab(tab_2x2, "Rubik 2x2")
        
        # Kết nối sự kiện khi chuyển tab
        tabs.currentChanged.connect(self.on_tab_changed)
        
        # Widget hiện tại (mặc định là 3x3)
        self.current_rubik_widget = self.rubik_widget_3x3
        
        # Thêm tabs vào layout chính
        main_layout.addWidget(tabs)

        # Dock widget bên phải cho controls
        dock = QDockWidget("Controls", self)
        dock.setFeatures(QDockWidget.NoDockWidgetFeatures)
        self.controls = ControlsWidget(self.current_rubik_widget)
        dock.setWidget(self.controls)
        self.addDockWidget(Qt.RightDockWidgetArea, dock)
        
        # Set kích thước cố định cho dock
        dock.setFixedWidth(300)
    
    def on_tab_changed(self, index):
        """Xử lý khi người dùng chuyển tab"""
        if index == 0:  # Rubik 3x3
            self.current_rubik_widget = self.rubik_widget_3x3
        else:  # Rubik 2x2
            self.current_rubik_widget = self.rubik_widget_2x2
        
        # Cập nhật widget hiện tại cho controls
        self.controls.set_rubik_widget(self.current_rubik_widget)

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()