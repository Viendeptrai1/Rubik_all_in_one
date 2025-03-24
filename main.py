import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from rubik_widget import RubikWidget
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

        # Widget trung tâm để render Rubik
        self.rubik_widget = RubikWidget()
        main_layout.addWidget(self.rubik_widget)

        # Dock widget bên phải cho controls
        dock = QDockWidget("Controls", self)
        dock.setFeatures(QDockWidget.NoDockWidgetFeatures)
        self.controls = ControlsWidget(self.rubik_widget)
        dock.setWidget(self.controls)
        self.addDockWidget(Qt.RightDockWidgetArea, dock)
        
        # Set kích thước cố định cho dock
        dock.setFixedWidth(300)

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()