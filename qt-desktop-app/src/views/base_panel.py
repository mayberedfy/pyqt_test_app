from PyQt6.QtWidgets import QMainWindow, QPushButton, QVBoxLayout, QWidget, QHBoxLayout
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QIcon
import os

class BasePanel(QMainWindow):
    def __init__(self, title):
        super().__init__()
        self.setWindowTitle(title)
        self.setGeometry(100, 100, 800, 600)
        
        # 设置窗口图标
        self.set_window_icon()

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        # 主垂直布局
        self.layout = QVBoxLayout(self.central_widget)
        
        # 在最顶部添加一个水平布局来放置返回按钮
        top_bar = QHBoxLayout()
        top_bar.setContentsMargins(0, 0, 0, 5)  # 设置上边距，与内容分隔
        
        # 创建返回按钮 - 美化版本
        self.back_button = QPushButton("← 返回主界面", self)
        self.back_button.setFixedSize(120, 36)  # 固定大小
        self.back_button.setCursor(Qt.CursorShape.PointingHandCursor)  # 鼠标悬停时显示手形光标
        self.back_button.setFont(QFont("Arial", 10, QFont.Weight.Bold))  # 设置粗体字
        
        # 设置按钮样式表
        self.back_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
                text-align: left;  /* 左对齐文本 */
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #1c6ea4;
            }
        """)
        
        self.back_button.clicked.connect(self.back_to_main)
        
        # 将按钮添加到顶部布局中，并在按钮后添加弹性空间
        top_bar.addWidget(self.back_button)
        top_bar.addStretch()  # 添加弹性空间，确保按钮靠左
        
        # 将顶部布局添加到主布局中
        self.layout.addLayout(top_bar)
        
        # 底部空白区域会被各个子类的内容填充

    def set_window_icon(self):
        """设置窗口图标"""
        # 获取资源路径
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        icon_path = os.path.join(base_path, "resources", "app_icon.png")
        
        # 如果图标存在，设置为窗口图标
        if os.path.exists(icon_path):
            app_icon = QIcon(icon_path)
            self.setWindowIcon(app_icon)

    def back_to_main(self):
        # 先清理资源
        self.cleanup()
        # 然后返回主界面
        from .main_window import MainWindow
        self.main_window = MainWindow()
        self.main_window.show()
        self.close()

    def cleanup(self):
        """清理资源的虚方法，由子类实现具体清理逻辑"""
        pass