from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QLabel, QPushButton, QWidget
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QSize
from views.base_panel import BasePanel
from views.components.serial_widget import SerialWidget
from views.components.motor_widget import MotorWidget
from controllers.serial_controller import SerialController


class MotorPanel(BasePanel):
    def __init__(self):
        super().__init__("电机板测试")

        # 创建串口处理对象
        self.serial_controller = SerialController()

        # 创建电机组件，传入串口控制器和串口组件
        self.motor_widget = MotorWidget(serial_controller=self.serial_controller)
        
        # 创建串口组件，传入串口控制器
        self.serial_widget = SerialWidget(serial_controller=self.serial_controller, motor_widget=self.motor_widget, parent_type="motor")
     
        # 设置电机组件与串口组件绑定
        self.motor_widget.serial_widget = self.serial_widget  


        # 添加到布局
        self.layout.addWidget(self.serial_widget)
        self.layout.addWidget(self.motor_widget)
        
        # 设置弹性布局
        self.layout.addStretch()


    def cleanup(self):
        # 确保串口关闭
        if self.serial_widget.is_open:
            self.serial_widget.toggle_serial()