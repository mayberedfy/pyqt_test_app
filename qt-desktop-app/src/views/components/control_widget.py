from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QDial, QPushButton, QFrame)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QPalette, QFont

from controllers.serial_controller import SerialController

class ControlWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        

        self.serial_controller = SerialController()


        # 创建主布局
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        
        # 创建旋钮区域标题
        knobs_title = QLabel("控制板档位显示")
        knobs_title.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.main_layout.addWidget(knobs_title)
        
        # 创建旋钮区域
        knobs_layout = QHBoxLayout()
        knobs_layout.setSpacing(40)  # 增加旋钮之间的间距
        
        # 创建速度旋钮组
        speed_knob_layout = QVBoxLayout()
        self.speed_knob = QDial()
        self.speed_knob.setMinimum(1)
        self.speed_knob.setMaximum(8)
        self.speed_knob.setNotchesVisible(True)
        self.speed_knob.setMinimumSize(120, 120)  # 增大旋钮尺寸
        self.speed_knob.valueChanged.connect(lambda: self.update_knob_label(self.speed_knob, self.speed_knob_label))
        self.speed_knob_label = QLabel("速度档位: 1")
        self.speed_knob_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.speed_knob_label.setFont(QFont("Arial", 14))  # 增大标签字体
        speed_knob_layout.addWidget(self.speed_knob)
        speed_knob_layout.addWidget(self.speed_knob_label)
        
        # 创建时间旋钮组
        time_knob_layout = QVBoxLayout()
        self.time_knob = QDial()
        self.time_knob.setMinimum(1)
        self.time_knob.setMaximum(8)
        self.time_knob.setNotchesVisible(True)
        self.time_knob.setMinimumSize(120, 120)  # 增大旋钮尺寸
        self.time_knob.valueChanged.connect(lambda: self.update_knob_label(self.time_knob, self.time_knob_label))
        self.time_knob_label = QLabel("时间档位: 1")
        self.time_knob_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.time_knob_label.setFont(QFont("Arial", 14))  # 增大标签字体
        time_knob_layout.addWidget(self.time_knob)
        time_knob_layout.addWidget(self.time_knob_label)
        
        # 添加旋钮到水平布局
        knobs_layout.addLayout(speed_knob_layout)
        knobs_layout.addLayout(time_knob_layout)
        
        # 创建指示灯区域
        lights_frame = QFrame()
        lights_frame.setFrameStyle(QFrame.Shape.Box)
        lights_frame_layout = QVBoxLayout(lights_frame)
        
        # 添加指示灯标题
        lights_title = QLabel("控制板灯光信号")
        lights_title.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        lights_frame_layout.addWidget(lights_title)
        
        # 创建指示灯布局
        lights_layout = QHBoxLayout()
        lights_layout.setSpacing(20)
        
        # 创建每个指示灯的垂直布局（包含标签和灯）
        green_layout = QHBoxLayout()
        green_label = QLabel("运行", self)
        self.green_light = self.create_light_button("", "green")
        green_layout.addWidget(green_label)
        green_layout.addWidget(self.green_light)
        
        blue_layout = QHBoxLayout()
        blue_label = QLabel("故障", self)
        self.blue_light = self.create_light_button("", "blue")
        blue_layout.addWidget(blue_label)
        blue_layout.addWidget(self.blue_light)
        
        red_layout = QHBoxLayout()
        red_label = QLabel("停机", self)
        self.red_light = self.create_light_button("", "red")
        red_layout.addWidget(red_label)
        red_layout.addWidget(self.red_light)
        
        # 添加所有灯光布局
        lights_layout.addLayout(green_layout)
        lights_layout.addLayout(blue_layout)
        lights_layout.addLayout(red_layout)
        lights_layout.addStretch()
        lights_frame_layout.addLayout(lights_layout)
        
        # 将所有组件添加到主布局
        self.main_layout.addLayout(knobs_layout)
        self.main_layout.addSpacing(20)
        self.main_layout.addWidget(lights_frame)
        self.main_layout.addStretch()

        self.blue_light.clicked.connect(self.on_blue_light_clicked)  
        self.red_light.clicked.connect(self.on_red_light_clicked)
        self.green_light.clicked.connect(self.on_green_light_clicked)  


    def update_knob_label(self, knob, label):
        if knob == self.speed_knob:
            label.setText(f"速度档位: {knob.value()}")
        elif knob == self.time_knob:
            label.setText(f"时间档位: {knob.value()}")

    def create_light_button(self, text, color):
        button = QPushButton(text)
        button.setMinimumSize(40, 40)
        button.setMaximumSize(40, 40)
        button.setCheckable(True)
        button.setStyleSheet("""
            QPushButton {
                border-radius: 20px;
                border: 2px solid #999;
            }
            QPushButton:checked {
                background-color: %s;
                border: 2px solid %s;
            }
        """ % (color, color))
        # button.clicked.connect(lambda: self.toggle_light(button))
        return button

    def toggle_light(self, clicked_button):
        # 获取所有灯按钮
        all_lights = [self.green_light, self.blue_light, self.red_light]
        
        # 如果点击的按钮被选中
        if clicked_button.isChecked():
            # 关闭其他所有灯
            for light in all_lights:
                if light != clicked_button:
                    light.setChecked(False)

 # 灯光点击事件处理
    def on_red_light_clicked(self):
        if self.red_light.isChecked():
            # 发送红灯对应的命令 (status = 0x00)
            command = "10 02 21 23 00 00 00 37 1C 00 00 A9 10 03"
            self.serial_controller.send_command(command)

    def on_blue_light_clicked(self):  # Changed from yellow
        if self.blue_light.isChecked():
            # 发送蓝灯对应的命令 (status = 0x20)
            command = "10 02 21 20 00 00 00 37 1C 00 00 C9 10 03"
            self.serial_controller.send_command(command)

    def on_green_light_clicked(self):  # Changed from blue
        if self.green_light.isChecked():
            # 发送绿灯对应的命令 (status = 0x0B)
            command = "10 02 21 23 0B 00 00 37 1C 00 00 B4 10 03"
            self.serial_controller.send_command(command)