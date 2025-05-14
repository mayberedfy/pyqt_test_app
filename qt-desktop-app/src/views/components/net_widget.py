from PyQt6.QtWidgets import (
    QWidget, QFrame, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QDial, QSizePolicy, QGroupBox, QSpinBox
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt, pyqtSignal


class NetWidget(QWidget):
    """网络联调界面组件"""
    
    # 定义信号
    start_clicked = pyqtSignal()
    stop_clicked = pyqtSignal()
    set_speed_clicked = pyqtSignal(int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 创建主布局 - 水平布局，包含三个模块
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(10)
        
        # 创建三个模块
        self._create_control_module()    # 网络控制模块
        self._create_controller_module() # 控制板信息模块
        self._create_motor_module()      # 电机信息模块
    
    def _create_control_module(self):
        """创建网络控制模块"""
        control_frame = QGroupBox("网络控制")
        control_frame.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        
        layout = QVBoxLayout(control_frame)
        layout.setContentsMargins(10, 15, 10, 10)
        layout.setSpacing(10)
        
        # 启动按钮
        self.start_button = QPushButton("启动")
        self.start_button.setFixedHeight(36)
        self.start_button.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        self.start_button.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                border-radius: 5px;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
            QPushButton:pressed {
                background-color: #1e8449;
            }
        """)
        self.start_button.clicked.connect(self.start_clicked)
        layout.addWidget(self.start_button)
        
        # 关闭按钮
        self.stop_button = QPushButton("关闭")
        self.stop_button.setFixedHeight(36)
        self.stop_button.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        self.stop_button.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border-radius: 5px;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
            QPushButton:pressed {
                background-color: #a93226;
            }
        """)
        self.stop_button.clicked.connect(self.stop_clicked)
        layout.addWidget(self.stop_button)
        
        # 调整电机转速行 - 包含按钮和输入框
        speed_layout = QHBoxLayout()
        
        # 调整电机转速按钮
        self.set_speed_button = QPushButton("调整电机转速")
        self.set_speed_button.setFixedHeight(36)
        self.set_speed_button.setFont(QFont("Arial", 10))
        self.set_speed_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border-radius: 5px;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #1c6ea4;
            }
        """)
        
        # 添加电机转速的输入框 - 范围是600到3450
        self.speed_input = QSpinBox()
        self.speed_input.setRange(600, 3450)
        self.speed_input.setSingleStep(50)
        self.speed_input.setValue(1200)  # 默认值
        self.speed_input.setSuffix(" RPM")
        self.speed_input.setFixedHeight(36)
        self.speed_input.setStyleSheet("""
            QSpinBox {
                border: 1px solid #bdc3c7;
                border-radius: 3px;
                padding: 2px 5px;
                background: white;
                min-width: 80px;
            }
            QSpinBox:hover {
                border: 1px solid #3498db;
            }
        """)
        
        # 修改按钮点击事件，使用输入框中的值
        self.set_speed_button.clicked.connect(self._on_set_speed_clicked)
        
        # 将按钮和输入框添加到水平布局
        speed_layout.addWidget(self.set_speed_button)
        speed_layout.addWidget(self.speed_input)
        
        # 将水平布局添加到主布局
        layout.addLayout(speed_layout)
        
        # 添加弹性空间
        layout.addStretch()
        
        # 将模块添加到主布局
        self.main_layout.addWidget(control_frame, 1)

    def _create_controller_module(self):
        """创建控制板信息模块"""
        controller_frame = QGroupBox("控制板信息")
        controller_frame.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        
        layout = QVBoxLayout(controller_frame)
        layout.setContentsMargins(10, 15, 10, 10)
        layout.setSpacing(15)
        
        # 创建两个旋钮的水平布局
        dials_layout = QHBoxLayout()
        
        # 速度档位旋钮
        speed_layout = QVBoxLayout()
        speed_layout.setSpacing(5)
        
        speed_label = QLabel("速度档位")
        speed_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        speed_layout.addWidget(speed_label)
        
        self.speed_dial = QDial()
        self.speed_dial.setMinimum(1)
        self.speed_dial.setMaximum(8)
        self.speed_dial.setValue(1)
        self.speed_dial.setNotchesVisible(True)
        self.speed_dial.setFixedSize(100, 100)
        self.speed_dial.setEnabled(False)  # 设为不可交互，仅显示
        self.speed_dial.setStyleSheet("""
            QDial {
                background-color: #f0f0f0;
                border: 2px solid #3498db;
                border-radius: 50px;
            }
        """)
        speed_layout.addWidget(self.speed_dial)
        
        self.speed_value_label = QLabel("1")
        self.speed_value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.speed_value_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        speed_layout.addWidget(self.speed_value_label)
        
        dials_layout.addLayout(speed_layout)
        
        # 时间档位旋钮
        time_layout = QVBoxLayout()
        time_layout.setSpacing(5)
        
        time_label = QLabel("时间档位")
        time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        time_layout.addWidget(time_label)
        
        self.time_dial = QDial()
        self.time_dial.setMinimum(1)
        self.time_dial.setMaximum(8)
        self.time_dial.setValue(1)
        self.time_dial.setNotchesVisible(True)
        self.time_dial.setFixedSize(100, 100)
        self.time_dial.setEnabled(False)  # 设为不可交互，仅显示
        self.time_dial.setStyleSheet("""
            QDial {
                background-color: #f0f0f0;
                border: 2px solid #3498db;
                border-radius: 50px;
            }
        """)
        time_layout.addWidget(self.time_dial)
        
        self.time_value_label = QLabel("1")
        self.time_value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.time_value_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        time_layout.addWidget(self.time_value_label)
        
        dials_layout.addLayout(time_layout)
        
        # 添加到主布局
        layout.addLayout(dials_layout)
        
        # 信号灯
        light_layout = QHBoxLayout()
        
        light_label = QLabel("信号灯:")
        light_label.setFont(QFont("Arial", 10))
        light_layout.addWidget(light_label)
        
        self.signal_light = QPushButton()
        self.signal_light.setFixedSize(80, 24)
        self.signal_light.setEnabled(False)
        self.signal_light.setStyleSheet("""
            QPushButton {
                border-radius: 5px;
                border: 1px solid #999;
                background-color: #f5f5f5;
            }
        """)
        light_layout.addWidget(self.signal_light)
        light_layout.addStretch()
        
        layout.addLayout(light_layout)
        layout.addStretch()
        
        # 将模块添加到主布局
        self.main_layout.addWidget(controller_frame, 1)
    
    def _create_motor_module(self):
        """创建电机信息模块"""
        motor_frame = QGroupBox("电机信息")
        motor_frame.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        
        layout = QVBoxLayout(motor_frame)
        layout.setContentsMargins(10, 15, 10, 10)
        layout.setSpacing(10)
        
        # 创建网格布局用于参数显示
        info_grid = QGridLayout()
        info_grid.setVerticalSpacing(10)
        info_grid.setHorizontalSpacing(10)
        
        # 系统状态
        info_grid.addWidget(QLabel("系统状态:"), 0, 0)
        self.status_label = QLabel("停止")
        self.status_label.setStyleSheet("QLabel { color: #2980b9; font-weight: bold; }")
        info_grid.addWidget(self.status_label, 0, 1)
        
        # 电机转速
        info_grid.addWidget(QLabel("电机转速:"), 1, 0)
        self.speed_label = QLabel("0 RPM")
        self.speed_label.setStyleSheet("QLabel { color: #2980b9; font-weight: bold; }")
        info_grid.addWidget(self.speed_label, 1, 1)
        
        # 电压值
        info_grid.addWidget(QLabel("电压值:"), 2, 0)
        self.voltage_label = QLabel("0 V")
        self.voltage_label.setStyleSheet("QLabel { color: #2980b9; font-weight: bold; }")
        info_grid.addWidget(self.voltage_label, 2, 1)
        
        # 温度值
        info_grid.addWidget(QLabel("温度值:"), 3, 0)
        self.temp_label = QLabel("0 °C")
        self.temp_label.setStyleSheet("QLabel { color: #2980b9; font-weight: bold; }")
        info_grid.addWidget(self.temp_label, 3, 1)
        
        # 输出功率
        info_grid.addWidget(QLabel("输出功率:"), 4, 0)
        self.power_label = QLabel("0 W")
        self.power_label.setStyleSheet("QLabel { color: #2980b9; font-weight: bold; }")
        info_grid.addWidget(self.power_label, 4, 1)
        
        layout.addLayout(info_grid)
        layout.addStretch()
        
        # 将模块添加到主布局
        self.main_layout.addWidget(motor_frame, 1)
    
    # 公共方法用于更新控件状态
    def set_controller_dials(self, speed_gear, time_gear):
        """设置控制板旋钮值"""
        self.speed_dial.setValue(speed_gear)
        self.speed_value_label.setText(str(speed_gear))
        
        self.time_dial.setValue(time_gear)
        self.time_value_label.setText(str(time_gear))
    
    def set_signal_light(self, color):
        """设置信号灯颜色
        color: 'red', 'green', 'blue' 或其他值表示灰色
        """
        if color == 'red':
            self.signal_light.setStyleSheet("""
                QPushButton {
                    border-radius: 5px;
                    border: 1px solid #d32f2f;
                    background-color: #f44336;
                }
            """)
        elif color == 'green':
            self.signal_light.setStyleSheet("""
                QPushButton {
                    border-radius: 5px;
                    border: 1px solid #388e3c;
                    background-color: #4caf50;
                }
            """)
        elif color == 'blue':
            self.signal_light.setStyleSheet("""
                QPushButton {
                    border-radius: 5px;
                    border: 1px solid #1565c0;
                    background-color: #2196f3;
                }
            """)
        else:
            self.signal_light.setStyleSheet("""
                QPushButton {
                    border-radius: 5px;
                    border: 1px solid #999;
                    background-color: #f5f5f5;
                }
            """)
    
    def update_motor_info(self, status="停止", speed=0, voltage=0.0, temp=0, power=0):
        """更新电机信息"""
        self.status_label.setText(status)
        self.speed_label.setText(f"{speed} RPM")
        self.voltage_label.setText(f"{voltage} V")
        self.temp_label.setText(f"{temp} °C")
        self.power_label.setText(f"{power} W")
        
        # 根据状态设置状态标签的颜色
        if "故障" in status:
            self.status_label.setStyleSheet("QLabel { color: #e74c3c; font-weight: bold; }")
        elif status == "运行":
            self.status_label.setStyleSheet("QLabel { color: #2ecc71; font-weight: bold; }")
        else:
            self.status_label.setStyleSheet("QLabel { color: #2980b9; font-weight: bold; }")
    
    def _on_set_speed_clicked(self):
        """当设置速度按钮被点击时，发送当前输入框中的值"""
        speed = self.speed_input.value()
        self.set_speed_clicked.emit(speed)