from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QFrame, QLineEdit, QSpinBox, QGridLayout, QMessageBox, QSizePolicy)  # 添加导入
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont


class MotorWidget(QWidget):
    def __init__(self, serial_controller=None, serial_widget=None, parent=None):
        super().__init__(parent)
        self.serial_controller = serial_controller
        self.serial_widget = serial_widget
        
        # 创建水平主布局而不是垂直布局
        self.main_layout = QHBoxLayout(self)  # 使用水平布局
        self.main_layout.setSpacing(10)  # 设置模块之间的间距
        self.main_layout.setContentsMargins(10, 10, 10, 10)  # 设置边距
        
        # 创建左右两个面板
        self._create_display_panel()  # 创建左侧显示面板（电机运行信息）
        self._create_speed_control_panel()  # 创建右侧控制面板（电机控制）

    def _create_display_panel(self):
        """创建左侧显示面板"""
        display_frame = QFrame()
        display_frame.setFrameStyle(QFrame.Shape.Box)
        display_frame.setMinimumWidth(300)  # 设置最小宽度
        display_frame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)  # 允许水平扩展
        
        display_layout = QVBoxLayout(display_frame)
        
        # 添加标题
        title = QLabel("电机运行信息")
        title.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        display_layout.addWidget(title)
        
        # 创建参数网格布局
        params_grid = QGridLayout()
        params_grid.setVerticalSpacing(10)
        params_grid.setHorizontalSpacing(15)
        
        # 添加五个运行参数显示
        self._add_param_row(params_grid, 0, "system_status", "系统状态", "停止")
        self._add_param_row(params_grid, 1, "motor_speed", "电机转速", "0 RPM")
        self._add_param_row(params_grid, 2, "voltage", "电压值", "0 V")
        self._add_param_row(params_grid, 3, "temperature", "温度值", "0 °C")
        self._add_param_row(params_grid, 4, "power", "输出功率", "0 W")
        
        display_layout.addLayout(params_grid)
        
        # 创建一个水平居中的容器用于放置读取状态按钮
        button_container = QHBoxLayout()
        button_container.addStretch()
        
        # 添加刷新按钮 - 放在参数标签的下方
        self.refresh_button = QPushButton("读取状态")
        self.refresh_button.clicked.connect(self._on_refresh_status)
        self.refresh_button.setFixedWidth(120)
        self.refresh_button.setFixedHeight(30)
        self.refresh_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border-radius: 5px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #1c6ea4;
            }
        """)
        
        button_container.addWidget(self.refresh_button)
        button_container.addStretch()
        
        # 添加按钮布局
        display_layout.addLayout(button_container)
        
        # 添加弹性空间在按钮下方
        display_layout.addStretch()
        
        # 添加到主布局，设置比例为1（左右各50%）
        self.main_layout.addWidget(display_frame, 1)

    def _add_param_row(self, grid_layout, row, label_name, name, default_value):
        """添加一行参数显示 (标签和值)"""
        # 参数名称
        name_label = QLabel(f"{name}:")
        name_label.setMinimumWidth(80)
        name_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        grid_layout.addWidget(name_label, row, 0)
        
        # 参数值 (保存为属性方便更新)
        value_label = QLabel(default_value)
        value_label.setStyleSheet("QLabel { color: #2980b9; font-weight: bold; }")
        value_label.setMinimumWidth(80)
        
        # 保存标签引用到对象属性中便于后续更新
        param_name = label_name.split()[0].lower() + "_label"
        setattr(self, param_name, value_label)
        
        grid_layout.addWidget(value_label, row, 1)
        

    def _create_speed_control_panel(self):
        """创建右侧速度控制面板"""
        control_frame = QFrame()
        control_frame.setFrameStyle(QFrame.Shape.Box)
        control_frame.setMinimumWidth(300)  # 设置最小宽度
        control_frame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)  # 允许水平扩展
        
        control_layout = QVBoxLayout(control_frame)
        control_layout.setContentsMargins(15, 15, 15, 15)  # 增加内边距
        
        # 1. 添加标题
        title = QLabel("电机控制")
        title.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)  # 居中对齐
        control_layout.addWidget(title)
        
        # 增加一点垂直间距
        control_layout.addSpacing(15)
        
        # 2. 创建转速设置行 - 包含设置按钮和输入框
        speed_setting_layout = QHBoxLayout()
        
        # 设置速度按钮
        self.send_button = QPushButton("设置转速")
        self.send_button.clicked.connect(self._on_send_speed)
        self.send_button.setStyleSheet("""
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
        speed_setting_layout.addWidget(self.send_button)
        
        # 转速输入框
        self.speed_input = QSpinBox()
        self.speed_input.setRange(600, 3450)
        self.speed_input.setSingleStep(50)
        self.speed_input.setSuffix(" RPM")
        self.speed_input.setValue(600)
        self.speed_input.setStyleSheet("""
            QSpinBox {
                font-size: 14px;
                padding: 2px;
                min-height: 25px;
            }
        """)
        speed_setting_layout.addWidget(self.speed_input)
        
        # 添加到主布局
        control_layout.addLayout(speed_setting_layout)
        
        # 增加一点垂直间距
        control_layout.addSpacing(15)
        
        # 3. 创建控制按钮行 - 启动和停止按钮
        control_buttons_layout = QHBoxLayout()
        
        # 启动按钮
        self.start_button = QPushButton("电机启动")
        self.start_button.clicked.connect(self._on_start)
        self.start_button.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                border-radius: 5px;
                padding: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
            QPushButton:pressed {
                background-color: #1e8449;
            }
        """)
        
        # 停止按钮
        self.stop_button = QPushButton("电机停止")
        self.stop_button.clicked.connect(self._on_stop)
        self.stop_button.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border-radius: 5px;
                padding: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
            QPushButton:pressed {
                background-color: #a93226;
            }
        """)
        
        # 添加到布局
        control_buttons_layout.addWidget(self.start_button)
        control_buttons_layout.addWidget(self.stop_button)
        
        # 添加到主布局
        control_layout.addLayout(control_buttons_layout)
        
        # 增加弹性空间
        control_layout.addStretch()
        
        # 创建指示灯区域 - 修改部分
        lights_frame = QFrame()
        lights_frame.setFrameStyle(QFrame.Shape.Box)
        lights_frame_layout = QVBoxLayout(lights_frame)
        lights_frame_layout.setContentsMargins(10, 10, 10, 15)  # 增加底部边距给标签留出空间

        # 添加指示灯标题
        lights_title = QLabel("电机板灯光信号")
        lights_title.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        lights_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lights_frame_layout.addWidget(lights_title)

        # 创建指示灯容器 - 使用HBox确保水平居中
        lights_container = QHBoxLayout()
        lights_container.setContentsMargins(0, 10, 0, 0)
        lights_container.addStretch(1)  # 左侧弹性空间

        # 创建指示灯布局
        lights_layout = QHBoxLayout()
        lights_layout.setSpacing(30)  # 增加灯之间的距离，使排布更均匀

        # 创建每个指示灯，现在直接在这个布局中而不是单独的垂直布局
        # 运行灯（绿色）
        self.green_light = self._create_light_button("", "green")
        lights_layout.addWidget(self.green_light)

        # 故障灯（蓝色）
        self.blue_light = self._create_light_button("", "blue")
        lights_layout.addWidget(self.blue_light)

        # 停机灯（红色）
        self.red_light = self._create_light_button("", "red")
        lights_layout.addWidget(self.red_light)

        # 添加灯光布局到容器
        lights_container.addLayout(lights_layout)
        lights_container.addStretch(1)  # 右侧弹性空间
        lights_frame_layout.addLayout(lights_container)

        # 创建标签容器 - 与灯对齐
        labels_container = QHBoxLayout()
        labels_container.setContentsMargins(0, 5, 0, 0)  # 与灯之间留出一点空间
        labels_container.addStretch(1)  # 左侧弹性空间

        # 创建标签布局 - 与灯光布局相同间距
        labels_layout = QHBoxLayout()
        labels_layout.setSpacing(30)  # 与灯之间相同的间距

        # 添加各标签，确保与灯对齐
        green_label = QLabel("运行")
        green_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        green_label.setFixedWidth(40)  # 与灯相同宽度
        labels_layout.addWidget(green_label)

        blue_label = QLabel("故障")
        blue_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        blue_label.setFixedWidth(40)  # 与灯相同宽度
        labels_layout.addWidget(blue_label)

        red_label = QLabel("停机")
        red_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        red_label.setFixedWidth(40)  # 与灯相同宽度
        labels_layout.addWidget(red_label)

        # 添加标签布局到容器
        labels_container.addLayout(labels_layout)
        labels_container.addStretch(1)  # 右侧弹性空间
        lights_frame_layout.addLayout(labels_container)

        control_layout.addWidget(lights_frame)
        
        self.main_layout.addWidget(control_frame, 1)
        
        # 初始化灯光状态，确保禁用点击功能
        self.current_light = None
        self.green_light.setEnabled(False)
        self.blue_light.setEnabled(False)
        self.red_light.setEnabled(False)

    def _create_light_button(self, text, color):
        """创建指示灯按钮 - 只用于显示，不可点击"""
        button = QPushButton(text)
        button.setMinimumSize(40, 40)
        button.setMaximumSize(40, 40)
        button.setCheckable(True)  # 保持可选中状态，但不响应点击
        button.setEnabled(False)   # 禁用按钮交互
        button.setStyleSheet("""
            QPushButton {
                border-radius: 20px;
                border: 2px solid #999;
                background-color: #eee;  /* 默认背景色 */
            }
            QPushButton:checked {
                background-color: %s;
                border: 2px solid %s;
            }
            /* 确保禁用后仍然显示颜色 */
            QPushButton:disabled:checked {
                background-color: %s;
                border: 2px solid %s;
            }
        """ % (color, color, color, color))
        return button

    def toggle_light(self, color):
        """切换灯光状态，确保只有一个灯能亮"""
        light_map = {
            'green': self.green_light,
            'blue': self.blue_light,
            'red': self.red_light
        }
        
        if color not in light_map:
            return
            
        target_light = light_map[color]
        
        # 如果目标灯已经是亮的，则不做任何操作
        if self.current_light == target_light and target_light.isChecked():
            return
            
        # 关闭其他所有灯
        for light in light_map.values():
            if light != target_light:
                light.setChecked(False)
        
        # 点亮目标灯
        target_light.setChecked(True)
        self.current_light = target_light

    def set_light_status(self, color):
        """从外部设置灯光状态"""
        self.toggle_light(color)


    def _on_stop(self):
        """停止电机"""
        if not self._check_serial_connection():
            return
            
        command = "10 02 80 00 00 92 10 03"
        self.serial_controller.send_command(command)
        
        # 连接信号处理器用于启动响应
        self.serial_controller.data_received.connect(self.handle_stop_response)

    def handle_stop_response(self, data):
        # 确认停止命令成功
        if len(data) >= 4 and data[2] == 0x80:
            # 处理停止成功
            print("电机停止命令已确认")
            
        # 断开此信号连接
        self.serial_controller.data_received.disconnect(self.handle_stop_response)
        
        # 发送读取状态命令获取最新状态
        # self._on_refresh_status()


    def _on_start(self):
        """启动电机"""
        if not self._check_serial_connection():
            return
            
        command = "10 02 81 00 00 93 10 03"
        self.serial_controller.send_command(command)
        self.system_status_label.setText("启动中...")
        
        # 连接信号处理器用于启动响应
        self.serial_controller.data_received.connect(self.handle_start_response)

    def handle_start_response(self, data):
        # 确认启动命令成功
        if len(data) >= 4 and data[2] == 0x81:
            # 处理启动成功
            print("电机启动命令已确认")
            
        # 断开此信号连接
        self.serial_controller.data_received.disconnect(self.handle_start_response)
        
        # 发送读取状态命令获取最新状态
        self._on_refresh_status()

    def _on_send_speed(self):
        """发送速度设定值"""
        if not self._check_serial_connection():
            return
            
        speed = self.speed_input.value()
        command = self.get_send_speed_command(speed)
        
        # 首先连接回调处理函数
        self.serial_controller.data_received.connect(self.handle_speed_response)
        
        # 然后发送命令
        self.serial_controller.send_command(command)
        
        # 不要在这里断开连接！断开连接应该在handle_speed_response中完成

    def get_send_speed_command(self, speed):
        if speed < 600 or speed > 3450:
            raise ValueError("速度值超出范围 (600-3450 RPM)")
        # 将速度值转为两个字节
        speed_high = (speed >> 8) & 0xFF
        speed_low = speed & 0xFF
        
        # 发送设置速度命令
        command = f"10 02 82 {speed_high:02X} {speed_low:02X} {(0x94 + speed_high + speed_low) & 0xFF:02X} 10 03"
        
        return command


    def handle_speed_response(self, data):
        # 确认速度设定命令成功
        if len(data) >= 4 and data[2] == 0x82:
            # 处理速度设定成功
            print("电机速度设定命令已确认")
            
        # 断开此信号连接
        self.serial_controller.data_received.disconnect(self.handle_speed_response)
        
        # 发送读取状态命令获取最新状态
        self._on_refresh_status()

    def send_command_with_response(self, command, callback):
        """
        发送命令并设置响应回调
        command: 要发送的命令字符串
        callback: 收到响应时调用的回调函数
        """
        # 先断开旧连接(如果有)
        try:
            self.serial_controller.data_received.disconnect()
        except:
            pass
        
        # 连接新回调
        self.serial_controller.data_received.connect(callback)
        
        # 发送命令
        self.serial_controller.send_command(command)

    def _on_refresh_status(self):
        """发送读取状态命令，获取电机即时状态"""
        # 检查串口是否打开
        if not self._check_serial_connection():
            return
        
        # 发送读系统参数命令
        command = "10 02 21 00 00 33 10 03"
        self.serial_controller.send_command(command)
        
        # 提示用户已发送读取命令
        self.system_status_label.setText("读取中...")
        self.motor_speed_label.setText("读取中...")
        self.voltage_label.setText("读取中...")
        self.temperature_label.setText("读取中...")
        self.power_label.setText("读取中...")

    def _check_serial_connection(self):
        """检查串口连接状态，如果未连接则显示提示"""
        if not self.serial_controller or not hasattr(self.serial_controller, 'serial_port') or \
           not self.serial_controller.serial_port or not self.serial_controller.serial_port.is_open:
            
            # 如果有serial_widget引用，可以直接检查其is_open属性
            if self.serial_widget and hasattr(self.serial_widget, 'is_open') and not self.serial_widget.is_open:
                QMessageBox.warning(self, "串口未连接", "请先连接串口后再进行操作。")
                return False
            
            # 备选检查方法
            if not self.serial_controller or not self.serial_controller.running:
                QMessageBox.warning(self, "串口未连接", "请先连接串口后再进行操作。")
                return False
                
            return False
        return True

    def handle_response_timeout(self):
        # 检查是否还在"读取中"状态
        if self.system_status_label.text() == "读取中...":
            self.system_status_label.setText("读取超时")
            self.motor_speed_label.setText("--")
            # ...其他状态恢复...
            
            # 断开信号连接
            try:
                self.serial_controller.data_received.disconnect(self.handle_data_received)
            except:
                pass

    def handle_data_received(self, data):
        # 解析数据并更新显示
        self.update_motor_info(data)
        
        # 断开信号连接
        self.serial_controller.data_received.disconnect(self.handle_data_received)
                 

    def update_motor_info(self, data):
        """根据接收到的数据更新电机信息
        data格式: [0x10, 0x02, 0x21, status, speed_high, speed_low, voltage_high, voltage_low, temp, power_high, power_low, checksum, 0x10, 0x03]
        """
        if len(data) >= 13:  # 确保数据长度足够
            # 提取状态
            status = data[3]
            status_text = "未知"
            if status == 0x00:
                status_text = "停止"
                self.set_light_status('red')
            elif status == 0x0B:
                status_text = "运行"
                self.set_light_status('green')
            elif status in [0x20, 0x21, 0x22, 0x23, 0x24, 0x25, 0x26, 0x27, 0x28, 0x29, 0x2A, 0x2B, 0x50]:
                # 故障代码映射字典
                fault_codes = {
                    0x20: "系统故障",
                    0x21: "15V电压低",
                    0x22: "DC过压",
                    0x23: "DC欠压",
                    0x24: "缺相",
                    0x25: "硬件过流",
                    0x26: "PCB过温",
                    0x27: "IPM过温",
                    0x28: "通讯失联",
                    0x29: "温度传感器故障",
                    0x2A: "软件过流",
                    0x2B: "堵转",
                    0x50: "未知故障"
                }
                                
                # 获取具体错误描述
                if status in fault_codes:
                    status_text = f"故障: {fault_codes[status]}"
                else:
                    status_text = "故障: 未定义错误"
                
                status_text = "故障"
                self.set_light_status('blue')
            
            # 更新系统状态标签
            self.system_status_label.setText(status_text)

            # 提取转速 (2字节)
            speed = (data[4] << 8) | data[5]
            self.motor_speed_label.setText(f"{speed} RPM")

            # 提取电压 (2字节)
            voltage = ((data[6] << 8) | data[7])
            self.voltage_label.setText(f"{voltage:.1f} V")

            # 提取温度 (1字节)
            temp = data[8]
            self.temperature_label.setText(f"{temp} °C")
            
            # 提取功率 (2字节)
            power = (data[9] << 8) | data[10]
            self.power_label.setText(f"{power} W")