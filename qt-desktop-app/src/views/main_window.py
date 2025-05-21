from PyQt6.QtWidgets import (QMainWindow, QPushButton, QVBoxLayout, 
                           QWidget, QLabel, QGridLayout, QSizePolicy)
from PyQt6.QtGui import QFont, QPixmap, QPalette, QBrush, QIcon, QPainter, QColor, QImage
from PyQt6.QtCore import Qt, QSize
import os

from .control_panel import ControlPanel
from .motor_panel import MotorPanel
from .net_panel import NetPanel

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # 设置窗口标题和大小
        self.setWindowTitle("1HP测试软件")
        self.setGeometry(100, 100, 800, 600)
        
        # 设置窗口图标
        self.set_window_icon()
        
        # 创建中央部件
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # 设置背景图片
        self.set_background_image()
        
        # 创建垂直布局
        self.layout = QVBoxLayout(self.central_widget)
        self.layout.setContentsMargins(0, 0, 0, 0)  # 移除边距以便使用对齐方式
        
        # 创建按钮容器 - 居中对齐
        button_container = QWidget()
        button_layout = QVBoxLayout(button_container)
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setSpacing(20)  # 按钮之间的间距
        button_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)  # 垂直居中
        
        # 添加三个按钮到按钮容器
        self.create_button("控制板测试", self.open_control_panel, button_layout)
        self.create_button("电机板测试", self.open_motor_panel, button_layout)
        self.create_button("网络联调", self.open_net_panel, button_layout)
        
        # 将按钮容器添加到主布局
        self.layout.addWidget(button_container, 1, Qt.AlignmentFlag.AlignCenter)
        
    def set_background_image(self):
        """设置窗口背景图片，并调整透明度"""
        # 获取资源路径
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        image_path = os.path.join(base_path, "resources", "industrial_background.png")
        
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
        else:
            # 创建 QPixmap 对象并加载图像
            pixmap = QPixmap(image_path)
            if not pixmap.isNull():
                # 创建一个 QImage 来调整透明度
                image = pixmap.toImage()
                # 使用 QPainter 在 QImage 上绘制半透明白色矩形来降低整体亮度
                painter = QPainter(image)
                painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceOver)
                # 使用白色半透明蒙版来减低透明度 - 调整最后的数字(0-255)来控制透明度
                # 数字越大，背景越淡
                painter.fillRect(image.rect(), QColor(255, 255, 255, 150))  # 透明度值：120/255
                painter.end()
                
                # 将修改后的图像设置回 pixmap
                modified_pixmap = QPixmap.fromImage(image)
                
                # 创建一个背景 brush
                brush = QBrush(modified_pixmap)
                # 创建一个自定义调色板
                palette = self.palette()
                # 设置背景
                palette.setBrush(QPalette.ColorRole.Window, brush)
                # 应用调色板
                self.setPalette(palette)
                
                # 确保背景图可见
                self.setAutoFillBackground(True)
        
    def create_button(self, text, callback, parent_layout):
        """创建适中矩形按钮"""
        button = QPushButton(text)
        
        # 设置字体
        button.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        
        # 设置尺寸 - 调短按钮长度
        button.setFixedSize(300, 80)  # 固定宽度和高度
        
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
        parent_layout.addWidget(button, 0, Qt.AlignmentFlag.AlignCenter)
        
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
        
    def set_window_icon(self):
        """设置窗口图标"""
        # 获取资源路径
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        icon_path = os.path.join(base_path, "resources", "app_icon.png")
        
        # 如果图标存在，设置为窗口图标
        if os.path.exists(icon_path):
            app_icon = QIcon(icon_path)
            self.setWindowIcon(app_icon)
        else:
            print(f"警告: 找不到图标文件: {icon_path}")