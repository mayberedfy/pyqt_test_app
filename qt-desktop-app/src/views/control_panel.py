from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QLabel, QPushButton, QWidget
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QSize
from .base_panel import BasePanel
from .components.serial_widget import SerialWidget
from .components.control_widget import ControlWidget
from controllers.serial_controller import SerialController

class ControlPanel(BasePanel):
    def __init__(self):
        super().__init__("控制板测试")
        self.setGeometry(100, 100, 800, 600)

        
        # 创建串口处理对象
        self.serial_controller = SerialController()
        
        # 先创建控制组件
        self.control_widget = ControlWidget(serial_controller=self.serial_controller)
        
        # 创建串口组件时传入控制组件
        self.serial_widget = SerialWidget(
            serial_controller=self.serial_controller,
            control_widget=self.control_widget,
            parent_type="control"
        )

        self.control_widget.set_serial_widget(self.serial_widget)
        # 添加到布局
        self.layout.addWidget(self.serial_widget)
        self.layout.addWidget(self.control_widget)

    def cleanup(self):
        # 确保串口关闭
        if self.serial_widget.is_open:
            self.serial_widget.toggle_serial()