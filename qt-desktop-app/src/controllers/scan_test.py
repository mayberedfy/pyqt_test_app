from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLineEdit, QTextEdit, QLabel
import sys

class ScanWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("扫码枪数据录入")
        self.resize(400, 300)

        self.layout = QVBoxLayout()

        self.label = QLabel("请用扫码枪扫描二维码，数据会显示在下方输入框：")
        self.layout.addWidget(self.label)

        self.input_line = QLineEdit()
        self.input_line.setPlaceholderText("扫码结果会显示在这里，按回车录入")
        self.layout.addWidget(self.input_line)

        self.result_box = QTextEdit()
        self.result_box.setReadOnly(True)
        self.result_box.setPlaceholderText("所有扫码结果记录：")
        self.layout.addWidget(self.result_box)

        self.setLayout(self.layout)

        # 绑定回车事件
        self.input_line.returnPressed.connect(self.record_scan)

    def record_scan(self):
        data = self.input_line.text().strip()
        if data:
            self.result_box.append(data)
            self.input_line.clear()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = ScanWindow()
    win.show()
    sys.exit(app.exec())