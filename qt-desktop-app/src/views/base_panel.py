from PyQt6.QtWidgets import QMainWindow, QPushButton, QVBoxLayout, QWidget
from PyQt6.QtCore import Qt

class BasePanel(QMainWindow):
    def __init__(self, title):
        super().__init__()
        self.setWindowTitle(title)
        self.setGeometry(100, 100, 800, 600)

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        # 主垂直布局
        self.layout = QVBoxLayout(self.central_widget)

        # 创建返回按钮
        self.back_button = QPushButton("返回主界面", self)
        self.back_button.clicked.connect(self.back_to_main)
        self.back_button.setGeometry(10, 10, 100, 30)

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