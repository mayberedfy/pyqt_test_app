from PyQt6.QtWidgets import QMainWindow, QPushButton
from .control_panel import ControlPanel
from .motor_panel import MotorPanel
from .net_panel import NetPanel

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("主界面")
        self.setGeometry(100, 100, 800, 600)

        # 设置按钮的通用配置
        button_width = 200
        button_height = 40
        button_x = 300
        button_start_y = 200
        button_spacing = 50

        # 控制板测试按钮
        self.control_button = QPushButton("控制板测试", self)
        self.control_button.clicked.connect(self.open_control_panel)
        self.control_button.setGeometry(button_x, button_start_y, button_width, button_height)

        # 电机板测试按钮
        self.motor_button = QPushButton("电机板测试", self)
        self.motor_button.clicked.connect(self.open_motor_panel)
        self.motor_button.setGeometry(button_x, button_start_y + button_spacing, button_width, button_height)

        # 网络联调联测按钮
        self.net_button = QPushButton("网络联调联测", self)
        self.net_button.clicked.connect(self.open_net_panel)
        self.net_button.setGeometry(button_x, button_start_y + button_spacing * 2, button_width, button_height)

    def open_control_panel(self):
        self.control_panel = ControlPanel()
        self.control_panel.show()
        self.hide()

    def open_motor_panel(self):
        self.motor_panel = MotorPanel()
        self.motor_panel.show()
        self.hide()

    def open_net_panel(self):
        self.net_panel = NetPanel()
        self.net_panel.show()
        self.hide()