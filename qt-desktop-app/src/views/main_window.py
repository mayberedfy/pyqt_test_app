from PyQt6.QtWidgets import QMainWindow, QPushButton
from .control_panel import ControlPanel
from .motor_panel import MotorPanel

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("主界面")
        self.setGeometry(100, 100, 800, 600)

        self.control_button = QPushButton("控制板测试", self)
        self.control_button.clicked.connect(self.open_control_panel)
        self.control_button.setGeometry(300, 250, 200, 40)

        self.motor_button = QPushButton("电机板测试", self)
        self.motor_button.clicked.connect(self.open_motor_panel)
        self.motor_button.setGeometry(300, 310, 200, 40)

    def open_control_panel(self):
        self.control_panel = ControlPanel()
        self.control_panel.show()
        self.hide()

    def open_motor_panel(self):
        self.motor_panel = MotorPanel()
        self.motor_panel.show()
        self.hide()