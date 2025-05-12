from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QFrame, QLineEdit, QSpinBox, QGridLayout)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont


class MotorWidget(QWidget):
    def __init__(self, serial_controller=None, parent=None):
        super().__init__(parent)
        self.serial_controller = serial_controller

        # 创建主布局
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(20)

        # 创建左右两个主要区域
        self._create_display_panel()
        self._create_speed_control_panel()

    def _create_display_panel(self):
        """创建左侧显示面板"""
        display_frame = QFrame()
        display_frame.setFrameStyle(QFrame.Shape.Box)
        display_frame.setMinimumWidth(300)
        
        display_layout = QVBoxLayout(display_frame)
        
        # 添加标题和刷新按钮的水平布局
        header_layout = QHBoxLayout()
        
        # 添加标题
        title = QLabel("电机运行信息")
        title.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        header_layout.addWidget(title)
        
        # 添加刷新按钮
        self.refresh_button = QPushButton("读取状态")
        self.refresh_button.clicked.connect(self._on_refresh_status)
        self.refresh_button.setFixedWidth(100)
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
        header_layout.addWidget(self.refresh_button)
        
        display_layout.addLayout(header_layout)
        
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
        display_layout.addStretch()
        
        self.main_layout.addWidget(display_frame)

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
        control_frame.setMinimumWidth(250)
        
        control_layout = QVBoxLayout(control_frame)
        
        # 添加标题
        title = QLabel("电机控制")
        title.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        control_layout.addWidget(title)
        
        # 添加速度输入框
        speed_layout = QHBoxLayout()
        speed_label = QLabel("目标转速:")
        self.speed_input = QSpinBox()
        self.speed_input.setRange(600, 3450)  # 修改转速范围为600-3450
        self.speed_input.setSingleStep(50)     # 更改步进值为50，更适合这个范围
        self.speed_input.setSuffix(" RPM")
        self.speed_input.setFixedWidth(120)
        self.speed_input.setValue(600)         # 设置初始值为最小值
        
        speed_layout.addWidget(speed_label)
        speed_layout.addWidget(self.speed_input)
        speed_layout.addStretch()
        
        # 添加控制按钮
        buttons_layout = QHBoxLayout()
        self.start_button = QPushButton("启动电机")
        self.start_button.clicked.connect(self._on_start)
        
        self.stop_button = QPushButton("停止电机")
        self.stop_button.clicked.connect(self._on_stop)
        
        buttons_layout.addWidget(self.start_button)
        buttons_layout.addWidget(self.stop_button)
        
        # 添加发送按钮
        self.send_button = QPushButton("设置速度")
        self.send_button.setFixedWidth(80)
        self.send_button.clicked.connect(self._on_send_speed)
        
        control_layout.addLayout(speed_layout)
        control_layout.addWidget(self.send_button)
        control_layout.addLayout(buttons_layout)
        control_layout.addStretch()
        
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
        
        # 创建每个指示灯的水平布局（包含标签和灯）
        green_layout = QHBoxLayout()
        green_label = QLabel("运行", self)
        self.green_light = self._create_light_button("", "green")
        green_layout.addWidget(green_label)
        green_layout.addWidget(self.green_light)
        
        blue_layout = QHBoxLayout()
        blue_label = QLabel("故障", self)
        self.blue_light = self._create_light_button("", "blue")
        blue_layout.addWidget(blue_label)
        blue_layout.addWidget(self.blue_light)
        
        red_layout = QHBoxLayout()
        red_label = QLabel("停机", self)
        self.red_light = self._create_light_button("", "red")
        red_layout.addWidget(red_label)
        red_layout.addWidget(self.red_light)
        
        # 添加所有灯光布局
        lights_layout.addLayout(green_layout)
        lights_layout.addLayout(blue_layout)
        lights_layout.addLayout(red_layout)
        lights_layout.addStretch()
        lights_frame_layout.addLayout(lights_layout)
        
        control_layout.addWidget(lights_frame)
        
        self.main_layout.addWidget(control_frame)
        
        # 初始化灯光状态
        self.current_light = None

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
        command = "10 02 80 00 00 92 10 03"
        # self.send_command_with_response(command, self.handle_stop_response)

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
        self._on_refresh_status()


    def _on_start(self):

        speed_command = self.get_send_speed_command(600)
        self.serial_controller.send_command(speed_command)

        command = "10 02 81 00 00 93 10 03"
        # self.send_command_with_response(command, self.handle_start_response)‘
        self.serial_controller.send_command(command)
    
        # 连接信号处理器用于启动响应
        self.serial_controller.data_received.connect(self.handle_start_response)
    
           # 更新UI状态
        self.system_status_label.setText("启动中...")

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
          
        # 提示用户已发送读取命令
        self.system_status_label.setText("读取中...")
        self.motor_speed_label.setText("读取中...")
        self.voltage_label.setText("读取中...")
        self.temperature_label.setText("读取中...")
        self.power_label.setText("读取中...")

        """发送读取状态命令，获取电机即时状态"""
        # 发送读系统参数命令
        command = "10 02 21 00 00 33 10 03"

        self.serial_controller.send_command(command)
        self.serial_controller.data_received.connect(self.handle_data_received)
        
        # 添加超时处理
        QTimer.singleShot(3000, self.handle_response_timeout)

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