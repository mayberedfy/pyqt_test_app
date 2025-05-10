from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QLabel, QPushButton, QWidget
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QSize
from .base_panel import BasePanel
from .components.serial_widget import SerialWidget

class MotorPanel(BasePanel):
    def __init__(self):
        super().__init__("电机板测试")
        
        # 添加串口设置组件
        self.serial_widget = SerialWidget()
        self.layout.addWidget(self.serial_widget)


    def cleanup(self):
        # 确保串口关闭
        if self.serial_widget.is_open:
            self.serial_widget.toggle_serial()