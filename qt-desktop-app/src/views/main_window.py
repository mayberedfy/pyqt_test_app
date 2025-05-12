from PyQt6.QtWidgets import (QMainWindow, QPushButton, QVBoxLayout, 
                           QWidget, QLabel, QGridLayout, QSizePolicy)
from PyQt6.QtGui import QFont, QPixmap, QPalette, QBrush, QIcon
from PyQt6.QtCore import Qt, QSize
import os

from .control_panel import ControlPanel
from .motor_panel import MotorPanel
from .net_panel import NetPanel

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # 设置窗口标题和大小
        self.setWindowTitle("工业设备测试系统")
        self.setGeometry(100, 100, 800, 600)
        
        # 创建中央部件
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # 设置背景图片
        self.set_background_image()
        
        # 创建垂直布局
        self.layout = QVBoxLayout(self.central_widget)
        self.layout.setContentsMargins(100, 50, 100, 50)  # 设置较大的左右边距
        self.layout.setSpacing(20)  # 按钮之间的间距
        
        # 添加标题
        # title = QLabel("工业设备测试系统")
        # title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # title.setFont(QFont("Arial", 26, QFont.Weight.Bold))
        # title.setStyleSheet("color: white; background-color: rgba(0,0,0,100);")
        # self.layout.addWidget(title)
        
        # 添加三个长矩形按钮
        self.create_button("控制板测试", self.open_control_panel)
        self.create_button("电机板测试", self.open_motor_panel)
        self.create_button("网络联调", self.open_net_panel)
        
        # 添加底部信息
        # footer = QLabel("© 2025 工业测控平台")
        # footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # footer.setFont(QFont("Arial", 10))
        # footer.setStyleSheet("color: white; background-color: rgba(0,0,0,100);")
        # self.layout.addWidget(footer)
        
        # 添加弹性空间
        self.layout.addStretch(1)  # 标题上方的弹性空间
        self.layout.addStretch(1)  # 页脚下方的弹性空间
        
    def set_background_image(self):
        """设置窗口背景图片"""
        # 获取资源路径
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        image_path = os.path.join(base_path, "resources", "industrial_background.jpg")
        
        # 如果图片不存在，使用默认样式
        if not os.path.exists(image_path):
            self.setStyleSheet("""
                QMainWindow {
                    background-color: qlineargradient(
                        x1: 0, y1: 0, x2: 1, y2: 1,
                        stop: 0 #2a5298, stop: 1 #1e3c72
                    );
                }
            """)
            return
            
        # 设置背景图片
        palette = QPalette()
        pixmap = QPixmap(image_path)
        brush = QBrush(pixmap.scaled(self.size(), Qt.AspectRatioMode.KeepAspectRatioByExpanding, 
                                    Qt.TransformationMode.SmoothTransformation))
        palette.setBrush(QPalette.ColorRole.Window, brush)
        self.setPalette(palette)
        
    def create_button(self, text, callback):
        """创建长矩形按钮"""
        button = QPushButton(text)
        
        # 设置字体
        button.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        
        # 设置尺寸
        button.setFixedHeight(80)  # 固定高度
        button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        
        # 设置样式
        button.setStyleSheet("""
            QPushButton {
                background-color: rgba(41, 128, 185, 200);
                color: white;
                border-radius: 10px;
                border: 2px solid #2980b9;
                padding: 10px;
                text-align: center;
            }
            QPushButton:hover {
                background-color: rgba(52, 152, 219, 200);
            }
            QPushButton:pressed {
                background-color: rgba(26, 82, 118, 200);
            }
        """)
        
        # 连接点击事件
        button.clicked.connect(callback)
        
        # 添加到布局
        self.layout.addWidget(button)
        
        return button

    def open_control_panel(self):
        self.control_panel = ControlPanel()
        self.control_panel.show()
        self.close()
        
    def open_motor_panel(self):
        self.motor_panel = MotorPanel()
        self.motor_panel.show()
        self.close()
        
    def open_net_panel(self):
        self.net_panel = NetPanel()
        self.net_panel.show()
        self.close()
        
    def resizeEvent(self, event):
        """窗口大小改变时，更新背景图片"""
        super().resizeEvent(event)
        self.set_background_image()