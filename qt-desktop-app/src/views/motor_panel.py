from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QLabel, QPushButton, QWidget
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QSize

class MotorPanel(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("电机板测试")
        self.setGeometry(100, 100, 800, 600)

        self.back_button = QPushButton("返回主界面", self)
        self.back_button.clicked.connect(self.back_to_main)
        self.back_button.setGeometry(10, 10, 100, 30)

    def back_to_main(self):
        from .main_window import MainWindow
        self.main_window = MainWindow()
        self.main_window.show()
        self.close()

