import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from rubik_widget import RubikWidget, RubikWidget2x2
from controls_widget import ControlsWidget
from csp_widget import CSPWidget

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Rubik All-in-One')
        self.resize(1600, 1000)

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
        
        # Tab cho CSP
        tab_csp = QWidget()
        layout_csp = QVBoxLayout()
        # Thay label tạm thời bằng CSP widget mới
        self.csp_widget = CSPWidget()
        layout_csp.addWidget(self.csp_widget)
        tab_csp.setLayout(layout_csp)
        
        # Thêm các tab vào tab widget
        tabs.addTab(tab_3x3, "Rubik 3x3")
        tabs.addTab(tab_2x2, "Rubik 2x2")
        tabs.addTab(tab_csp, "CSP")
        
        # Kết nối sự kiện khi chuyển tab
        tabs.currentChanged.connect(self.on_tab_changed)
        
        # Widget hiện tại (mặc định là 3x3)
        self.current_rubik_widget = self.rubik_widget_3x3
        
        # Thêm tabs vào layout chính
        main_layout.addWidget(tabs)

        # Dock widget bên phải cho controls
        self.dock = QDockWidget("Điều khiển", self)
        self.dock.setFeatures(QDockWidget.NoDockWidgetFeatures)
        self.controls = ControlsWidget(self.current_rubik_widget)
        self.dock.setWidget(self.controls)
        self.addDockWidget(Qt.RightDockWidgetArea, self.dock)
        
        # Set kích thước cố định cho dock
        self.dock.setFixedWidth(700)
    
    def on_tab_changed(self, index):
        """Xử lý khi người dùng chuyển tab"""
        if index == 0:  # Rubik 3x3
            self.current_rubik_widget = self.rubik_widget_3x3
            self.controls.setVisible(True)
            self.dock.setVisible(True)
        elif index == 1:  # Rubik 2x2
            self.current_rubik_widget = self.rubik_widget_2x2
            self.controls.setVisible(True)
            self.dock.setVisible(True)
        else:  # CSP
            # Ẩn hoàn toàn dock widget khi ở tab CSP để CSP widget sử dụng toàn bộ không gian
            self.dock.setVisible(False)
            return
            
        # Chỉ cập nhật widget controls nếu đang ở tab Rubik
        if index < 2:
            self.controls.set_rubik_widget(self.current_rubik_widget)

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()