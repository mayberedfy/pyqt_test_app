from PyQt6.QtWidgets import QVBoxLayout, QWidget, QPushButton
from PyQt6.QtCore import Qt, pyqtSlot

from .base_panel import BasePanel
from .components.mqtt_widget import MqttWidget
from .components.net_widget import NetWidget


class NetPanel(BasePanel):
    """网络联调面板"""
    
    def __init__(self):
        super().__init__("网络联调")
        self.init_ui()
        
    def init_ui(self):
        # 创建内容区域的容器
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(10, 10, 10, 10)
        content_layout.setSpacing(15)  # 组件之间的垂直间距
        
        # 添加 MQTT 组件
        self.mqtt_widget = MqttWidget()
        content_layout.addWidget(self.mqtt_widget)
        
        # 添加 Net 组件
        self.net_widget = NetWidget()
        content_layout.addWidget(self.net_widget)
        
        # 将内容添加到基本面板的主布局中
        self.layout.addWidget(content_widget)
        
        # 连接信号和槽
        self.connect_signals()
        
    def connect_signals(self):
        """连接所有组件的信号"""
        # 连接 NetWidget 信号到对应的槽函数
        self.net_widget.start_clicked.connect(self.on_start_clicked)
        self.net_widget.stop_clicked.connect(self.on_stop_clicked)
        self.net_widget.set_speed_clicked.connect(self.on_set_speed)
        
        # 可以在此处添加 MQTT 相关的信号连接
        
    @pyqtSlot()
    def on_start_clicked(self):
        """处理启动按钮点击事件"""
        print("网络控制: 启动")
        # 启动相关操作
        self.net_widget.set_signal_light('green')
        self.net_widget.update_motor_info(status="运行", speed=1200, voltage=220.0, temp=25, power=100)
        
    @pyqtSlot()
    def on_stop_clicked(self):
        """处理关闭按钮点击事件"""
        print("网络控制: 关闭")
        # 停止相关操作
        self.net_widget.set_signal_light('red')
        self.net_widget.update_motor_info(status="停止", speed=0, voltage=0.0, temp=0, power=0)
        
    @pyqtSlot(int)
    def on_set_speed(self, speed):
        """处理设置转速事件"""
        print(f"设置电机转速: {speed} RPM")
        # 设置转速相关操作
        self.net_widget.update_motor_info(status="运行", speed=speed, voltage=220.0, temp=28, power=120)
        
        # 假设根据速度设置不同的档位
        if speed <= 800:
            self.net_widget.set_controller_dials(1, 3)
        elif speed <= 1500:
            self.net_widget.set_controller_dials(2, 3)
        elif speed <= 2200:
            self.net_widget.set_controller_dials(3, 4)
        elif speed <= 3000:
            self.net_widget.set_controller_dials(4, 5)
        else:
            self.net_widget.set_controller_dials(5, 5)
 
        
    def cleanup(self):
        """清理资源"""
        # 确保 MQTT 客户端断开连接
        if hasattr(self, 'mqtt_widget'):
            self.mqtt_widget.cleanup()
