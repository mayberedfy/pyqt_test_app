from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QDial, QPushButton, QFrame, QComboBox)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor, QPalette, QFont


class ControlWidget(QWidget):
    def __init__(self, serial_controller=None, serial_widget=None, parent=None):
        super().__init__(parent)

        self.serial_controller = serial_controller
        self.serial_widget = serial_widget
        
        # 添加定时器用于持续发送命令
        self.command_timer = QTimer(self)
        self.command_timer.timeout.connect(self.send_current_command)
        self.current_command_type = None  # 'start', 'stop', 'fault' 或 None
        self.current_fault_code = None    # 只有在故障模式下才使用
        
        self._create_ui()
        
        
        # 如果有serial_widget，则监听其串口状态变化
        if self.serial_widget:
            # 初始检查串口状态
            self.update_lights_clickable_state()
        
        # # 强制立即检查串口状态
        # self.force_update_lights_state()


    def _create_ui(self):
        """创建用户界面"""
        # 主布局保持不变
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(15)
        
        # ===== 左侧：旋钮控制区域 =====
        knobs_frame = QFrame()
        knobs_frame.setFrameStyle(QFrame.Shape.Box)
        knobs_layout = QVBoxLayout(knobs_frame)
        knobs_layout.setContentsMargins(15, 15, 15, 15)
        
        # 旋钮区域标题
        knobs_title = QLabel("旋钮控制")
        knobs_title.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        knobs_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        knobs_layout.addWidget(knobs_title)
        
        # 创建速度控制旋钮
        speed_layout = QVBoxLayout()
        speed_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.speed_knob_label = QLabel("速度档位: 1")
        self.speed_knob_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.speed_knob_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        
        self.speed_knob = self._create_knob("速度档位", 1, 8)
        self.speed_knob.valueChanged.connect(lambda value: self.update_knob_label(self.speed_knob, self.speed_knob_label))
        
        speed_layout.addWidget(self.speed_knob)
        speed_layout.addWidget(self.speed_knob_label)
        
        # 创建时间控制旋钮
        time_layout = QVBoxLayout()
        time_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.time_knob_label = QLabel("时间档位: 1")
        self.time_knob_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.time_knob_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        
        self.time_knob = self._create_knob("时间档位", 1, 8)
        self.time_knob.valueChanged.connect(lambda value: self.update_knob_label(self.time_knob, self.time_knob_label))
        
        time_layout.addWidget(self.time_knob)
        time_layout.addWidget(self.time_knob_label)
        
        # 水平排列两个旋钮
        knobs_container = QHBoxLayout()
        knobs_container.addLayout(speed_layout)
        knobs_container.addLayout(time_layout)
        knobs_layout.addLayout(knobs_container)
        knobs_layout.addStretch()
        
        # ===== 右侧：控制区域 =====
        control_frame = QFrame()
        control_frame.setFrameStyle(QFrame.Shape.Box)
        control_layout = QVBoxLayout(control_frame)
        control_layout.setContentsMargins(15, 15, 15, 15)
        # 减小间距从25到12，使布局更紧凑
        control_layout.setSpacing(12)  
        
        # ===== 第一部分：灯光信号 =====
        light_panel = QHBoxLayout()
        light_panel.setSpacing(15)
        
        # 左侧标签
        light_label = QLabel("控制板正确显示灯光：")
        light_label.setFont(QFont("Arial", 11, QFont.Weight.Normal))
        light_label.setFixedWidth(120)
        light_panel.addWidget(light_label)
        
        # 右侧单盏灯
        self.signal_light = QPushButton("")
        self.signal_light.setFixedSize(50, 50)  # 减小高度从60到50，使布局更紧凑
        self.signal_light.setCheckable(True)
        self.signal_light.setStyleSheet("""
            QPushButton {
                border-radius: 10px;
                border: 2px solid #999;
                background-color: #f5f5f5;
            }
        """)
        self.signal_light.setEnabled(False)
        light_panel.addWidget(self.signal_light)
        light_panel.addStretch()
        
        control_layout.addLayout(light_panel)
        
        # 减小间隔空间高度从5到2
        spacer1 = QWidget()
        spacer1.setFixedHeight(2)
        control_layout.addWidget(spacer1)
        
        # ===== 第二部分：电机运行/停机按钮 =====
        operation_panel = QHBoxLayout()
        operation_panel.setSpacing(20)
        
        # 电机运行按钮 - 添加绿色样式
        self.start_button = QPushButton("电机运行")
        self.start_button.setFixedHeight(40)
        self.start_button.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        self.start_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;  /* 绿色 */
                color: white;
                border-radius: 5px;
                border: none;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
            QPushButton:disabled {
                background-color: #c8e6c9;
                color: #a5d6a7;
            }
        """)
        self.start_button.clicked.connect(self.on_motor_start)
        operation_panel.addWidget(self.start_button)
        
        # 电机停机按钮 - 添加红色样式
        self.stop_button = QPushButton("电机停机")
        self.stop_button.setFixedHeight(40)
        self.stop_button.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        self.stop_button.setStyleSheet("""
            QPushButton {
                background-color: #f44336;  /* 红色 */
                color: white;
                border-radius: 5px;
                border: none;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
            QPushButton:pressed {
                background-color: #b71c1c;
            }
            QPushButton:disabled {
                background-color: #ffcdd2;
                color: #ef9a9a;
            }
        """)
        self.stop_button.clicked.connect(self.on_motor_stop)
        operation_panel.addWidget(self.stop_button)
        
        control_layout.addLayout(operation_panel)
        
        # 减小间隔空间高度
        spacer2 = QWidget()
        spacer2.setFixedHeight(2)
        control_layout.addWidget(spacer2)
        
        # ===== 第三部分：故障部分 =====
        fault_panel = QHBoxLayout()
        
        # 电机故障按钮 - 添加蓝色样式
        self.fault_button = QPushButton("电机故障")
        self.fault_button.setFixedHeight(40)
        # self.fault_button.setFixedWidth(120)
        self.fault_button.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        self.fault_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;  /* 蓝色 */
                color: white;
                border-radius: 5px;
                border: none;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #0D47A1;
            }
            QPushButton:disabled {
                background-color: #BBDEFB;
                color: #90CAF9;
            }
        """)
        self.fault_button.clicked.connect(self.on_motor_fault)
        fault_panel.addWidget(self.fault_button)
        
        # 故障类型下拉框 - 减小高度
        self.fault_selector = QComboBox()
        self.fault_selector.setFixedHeight(36)  # 从40减小到36
        self.fault_selector.addItems([
            "系统故障",
            "15V电压低",
            "DC过压",
            "DC欠压",
            "缺相",
            "硬件过流",
            "PCB过温",
            "IPM过温",
            "通讯失联",
            "温度传感器故障",
            "软件过流",
            "堵转",
            "未知故障"
        ])
        self.fault_selector.setStyleSheet("""
            QComboBox {
                padding: 5px 10px;
                border: 1px solid #ccc;
                border-radius: 5px;
                background-color: #ffffff;
                font-size: 11pt;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 25px;
                border-left: 1px solid #ccc;
            }
        """)
        fault_panel.addWidget(self.fault_selector)
        
        control_layout.addLayout(fault_panel)
        
        # 减小添加的弹性空间，使内容总体上移
        control_layout.addStretch(1)  # 使用整数值作为弹性空间权重
        
        # 添加面板到主布局，比例为1:1
        main_layout.addWidget(knobs_frame, 1)
        main_layout.addWidget(control_frame, 1)
        
        # 初始化所有按钮的状态
        self.update_button_states()



    def _create_knob(self, name, min_value, max_value):
        """创建旋钮控件 - 更大且禁用交互"""
        knob = QDial()
        knob.setMinimum(min_value)
        knob.setMaximum(max_value)
        knob.setValue(min_value)
        knob.setNotchesVisible(True)
        knob.setWrapping(False)
        knob.setFixedSize(160, 160)  # 增大尺寸从80x80到120x120
        knob.setEnabled(False)  # 禁用交互
        knob.setStyleSheet("""
            QDial {
                background-color: #f0f0f0;
                border: 2px solid #3498db;
                border-radius: 60px;
            }
        """)
        return knob
    
    def update_knob_label(self, knob, label):
        if knob == self.speed_knob:
            label.setText(f"速度档位: {knob.value()}")
        elif knob == self.time_knob:
            label.setText(f"时间档位: {knob.value()}")

  
    def set_serial_widget(self, serial_widget):
        """设置与此控件关联的串口部件，并更新状态"""
        self.serial_widget = serial_widget
        if self.serial_widget:
            self.update_lights_clickable_state()


    def set_signal_light(self, color):
        """设置信号灯颜色"""
        if color == "red":
            self.signal_light.setStyleSheet("""
                QPushButton {
                    border-radius: 10px;  /* 使用较小的圆角 */
                    border: 2px solid #d32f2f;
                    background-color: #f44336;
                }
            """)
        elif color == "green":
            self.signal_light.setStyleSheet("""
                QPushButton {
                    border-radius: 10px;  /* 使用较小的圆角 */
                    border: 2px solid #388e3c;
                    background-color: #4caf50;
                }
            """)
        elif color == "blue":
            self.signal_light.setStyleSheet("""
                QPushButton {
                    border-radius: 10px;  /* 使用较小的圆角 */
                    border: 2px solid #1565c0;
                    background-color: #2196f3;
                }
            """)
        else:  # 默认灰色
            self.signal_light.setStyleSheet("""
                QPushButton {
                    border-radius: 10px;  /* 使用较小的圆角 */
                    border: 2px solid #999;
                    background-color: #f5f5f5;
                }
            """)


    # 处理命令5# 读系统参数：
    # 发送：CMD = 0x21  DATA0 = 0 	DATA1 = 0
    # 应答：格式同发送
    # DATA0：系统状态
    # DATA1~DATA2：电机转速值
    # DATA3~DATA4：电压值
    # DATA5：IPM温度值
    # DATA6~DATA7：输出功率值 
    # response = "10 02 21 23 00 00 00 37 1C 00 00 A9 10 03"

    def on_motor_start(self):
        """处理电机运行按钮点击事件 - 持续发送运行命令"""
        if self.serial_controller:
            # 停止任何正在进行的命令发送
            self.stop_sending_commands()
            
            # 设置当前命令类型为启动
            self.current_command_type = 'start'
            
            # 立即发送一次命令
            self.send_current_command()

            # 启动定时器，每50ms发送一次命令
            self.command_timer.start(50)
            
            # 更新UI
            self.set_signal_light("green")  # 设置绿灯表示运行
            self.update_button_highlighting()

    def on_motor_stop(self):
        """处理电机停机按钮点击事件 - 持续发送停止命令"""
        if self.serial_controller:
            # 停止任何正在进行的命令发送
            self.stop_sending_commands()
            
            # 设置当前命令类型为停止
            self.current_command_type = 'stop'
            
            # 立即发送一次命令
            self.send_current_command()
            
            # 启动定时器，每50ms发送一次命令
            self.command_timer.start(50)
            
            # 更新UI
            self.set_signal_light("red")  # 设置红灯表示停止
            self.update_button_highlighting()

    def on_motor_fault(self):
        """处理电机故障按钮点击事件 - 持续发送故障命令"""
        if self.serial_controller:
            # 停止任何正在进行的命令发送
            self.stop_sending_commands()
            
            # 获取故障类型
            fault_index = self.fault_selector.currentIndex()
            # 计算故障代码 (0x20-0x2B, 0x50)
            fault_code = 0x20 + fault_index
            if fault_index >= 12:  # 未知故障
                fault_code = 0x50
            
            # 保存当前故障代码
            self.current_fault_code = fault_code
            
            # 设置当前命令类型为故障
            self.current_command_type = 'fault'
            
            # 立即发送一次命令
            self.send_current_command()
            
            # 启动定时器，每500ms发送一次命令
            self.command_timer.start(500)
            
            # 更新UI
            self.set_signal_light("blue")  # 设置蓝灯表示故障
            self.update_button_highlighting()

    def get_checksum(self, command):
        checksum = 0
        for byte in command.split():
            checksum += int(byte, 16)
        checksum = checksum & 0xFF  
        print("checksum:", hex(checksum))
        return checksum

    def send_current_command(self):
        """根据当前命令类型发送相应的命令"""
        if not self.serial_controller or self.current_command_type is None:
            return
            
        if self.current_command_type == 'start':
            pre_command = "10 02 21 0B 00 00 00 37 1C 00 00" 
            checksum = self.get_checksum(pre_command) 
            command = f"10 02 21 0B 00 00 00 37 1C 00 00 {checksum:02X} 10 03"
            self.serial_controller.send_command(command)
            
        elif self.current_command_type == 'stop':
            pre_command = "10 02 21 00 00 00 00 37 1C 00 00"
            checksum = self.get_checksum(pre_command)
            command = f"10 02 21 00 00 00 00 37 1C 00 00 {checksum:02X} 10 03"
            self.serial_controller.send_command(command)
            
        elif self.current_command_type == 'fault' and self.current_fault_code is not None:
            pre_command = f"10 02 21 {self.current_fault_code:02X} 00 00 00 00 00 00 00"
            checksum = self.get_checksum(pre_command)
            command = f"10 02 21 {self.current_fault_code:02X} 00 00 00 00 00 00 00 {checksum:02X} 10 03"
            self.serial_controller.send_command(command)

    def stop_sending_commands(self):
        """停止发送命令"""
        if self.command_timer.isActive():
            self.command_timer.stop()
        self.current_command_type = None
        self.current_fault_code = None
        self.update_button_highlighting()

    def update_button_highlighting(self):
        """根据当前命令类型更新按钮高亮状态"""
        # 重置所有按钮的默认样式
        self.reset_button_styles()
        
        # 根据当前命令类型高亮对应按钮
        if self.current_command_type == 'start':
            self.start_button.setStyleSheet("""
                QPushButton {
                    background-color: #2ecc71;  /* 更亮的绿色 */
                    color: white;
                    border-radius: 5px;
                    border: 2px solid #27ae60;  /* 添加边框突出显示 */
                    padding: 8px 16px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #27ae60;
                }
                QPushButton:pressed {
                    background-color: #1e8449;
                }
                QPushButton:disabled {
                    background-color: #c8e6c9;
                    color: #a5d6a7;
                }
            """)
        elif self.current_command_type == 'stop':
            self.stop_button.setStyleSheet("""
                QPushButton {
                    background-color: #e74c3c;  /* 更亮的红色 */
                    color: white;
                    border-radius: 5px;
                    border: 2px solid #c0392b;  /* 添加边框突出显示 */
                    padding: 8px 16px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #c0392b;
                }
                QPushButton:pressed {
                    background-color: #a93226;
                }
                QPushButton:disabled {
                    background-color: #ffcdd2;
                    color: #ef9a9a;
                }
            """)
        elif self.current_command_type == 'fault':
            self.fault_button.setStyleSheet("""
                QPushButton {
                    background-color: #2196F3;  /* 更亮的蓝色 */
                    color: white;
                    border-radius: 5px;
                    border: 2px solid #1976D2;  /* 添加边框突出显示 */
                    padding: 8px 16px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #1976D2;
                }
                QPushButton:pressed {
                    background-color: #0D47A1;
                }
                QPushButton:disabled {
                    background-color: #BBDEFB;
                    color: #90CAF9;
                }
            """)

    def reset_button_styles(self):
        """重置按钮样式到默认状态"""
        # 电机运行按钮 - 绿色样式
        self.start_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;  /* 绿色 */
                color: white;
                border-radius: 5px;
                border: none;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
            QPushButton:disabled {
                background-color: #c8e6c9;
                color: #a5d6a7;
            }
        """)
        
        # 电机停机按钮 - 红色样式
        self.stop_button.setStyleSheet("""
            QPushButton {
                background-color: #f44336;  /* 红色 */
                color: white;
                border-radius: 5px;
                border: none;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
            QPushButton:pressed {
                background-color: #b71c1c;
            }
            QPushButton:disabled {
                background-color: #ffcdd2;
                color: #ef9a9a;
            }
        """)
        
        # 电机故障按钮 - 蓝色样式
        self.fault_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;  /* 蓝色 */
                color: white;
                border-radius: 5px;
                border: none;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #0D47A1;
            }
            QPushButton:disabled {
                background-color: #BBDEFB;
                color: #90CAF9;
            }
        """)

    def update_button_states(self):
        """根据串口连接状态更新按钮状态"""
        is_connected = False
        if self.serial_widget and hasattr(self.serial_widget, 'is_open'):
            is_connected = self.serial_widget.is_open
            
        self.start_button.setEnabled(is_connected)
        self.stop_button.setEnabled(is_connected)
        self.fault_button.setEnabled(is_connected)
        self.fault_selector.setEnabled(is_connected)
        
        # 如果串口断开，停止发送命令
        if not is_connected:
            self.stop_sending_commands()

    def update_lights_clickable_state(self):
        """根据串口连接状态更新按钮可用性"""
        self.update_button_states()
