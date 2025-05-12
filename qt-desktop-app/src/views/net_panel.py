from PyQt6.QtWidgets import QPushButton, QWidget, QVBoxLayout
from PyQt6.QtCore import Qt
from .base_panel import BasePanel
from .components.mqtt_widget import MqttWidget

class NetPanel(BasePanel):
    def __init__(self):
        super().__init__("网络联调联测")
        
        # 调整返回按钮的位置和大小
        # 注意：back_button是在BasePanel中创建的，这里只是调整它
        self.back_button.setGeometry(10, 10, 100, 30)
        
        # 添加 MQTT 组件
        self.mqtt_widget = MqttWidget()
        
        # 调整MQTT组件距离顶部的边距，留出返回按钮的空间
        # 方法1: 直接给MQTT组件的布局增加上边距
        self.mqtt_widget.main_layout.setContentsMargins(10, 50, 10, 10)
        
        # 将MQTT组件添加到面板布局
        self.layout.addWidget(self.mqtt_widget)
        
        # 设置布局的对齐方式，使组件紧凑排列
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)

    def cleanup(self):
        """清理资源"""
        # 确保 MQTT 客户端断开连接
        if hasattr(self, 'mqtt_widget'):
            self.mqtt_widget.cleanup()
