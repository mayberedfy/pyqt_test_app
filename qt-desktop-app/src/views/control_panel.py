from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QLabel, QPushButton, QWidget
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QSize
from .base_panel import BasePanel
from .components.serial_widget import SerialWidget
from .components.control_widget import ControlWidget

class ControlPanel(BasePanel):
    def __init__(self):
        super().__init__("控制板测试")
        self.setGeometry(100, 100, 800, 600)
        
        # 先创建控制组件
        self.control_widget = ControlWidget()
        
        # 创建串口组件时传入控制组件
        self.serial_widget = SerialWidget(control_widget=self.control_widget)
        
        # 添加到布局
        self.layout.addWidget(self.serial_widget)
        self.layout.addWidget(self.control_widget)

    def cleanup(self):
        # 确保串口关闭
        if self.serial_widget.is_open:
            self.serial_widget.toggle_serial()


