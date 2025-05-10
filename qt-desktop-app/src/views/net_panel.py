from PyQt5.QtWidgets import QPushButton, QWidget
from .base_panel import BasePanel

class NetPanel(BasePanel):
    def __init__(self):
        super().__init__("网络联调联测")

    #     self.back_button = QPushButton("返回主界面", self)
    #     self.back_button.clicked.connect(self.back_to_main)
    #     self.back_button.setGeometry(10, 10, 100, 30)

    # def back_to_main(self):
    #     from .main_window import MainWindow
    #     self.main_window = MainWindow()
    #     self.main_window.show()
    #     self.close()
