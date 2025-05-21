from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QFrame, QLineEdit, QSpinBox, QGridLayout, QMessageBox, QSizePolicy)  # 添加导入
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont

class MotorWidget(QWidget):
    def __init__(self, serial_controller=None, serial_widget=None, serial_data_controller=None, parent=None):
        super().__init__(parent)
        self.serial_controller = serial_controller

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
        
        
        params_grid = QGridLayout()
        params_grid.setVerticalSpacing(10)
        params_grid.setHorizontalSpacing(15)
        
        # 创建一个容器widget来装载网格布局
        params_container = QWidget()
        params_container.setLayout(params_grid)
        params_container.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        
        # 使用水平布局包裹容器widget以实现水平居中
        params_wrapper = QHBoxLayout()
        params_wrapper.addStretch(1)  # 左侧弹性空间
        params_wrapper.addWidget(params_container)
        params_wrapper.addStretch(1)  # 右侧弹性空间
        
        # 将水平包装布局添加到display_layout
        display_layout.addLayout(params_wrapper)
        # 添加系统状态显示
        self._add_param_row(params_grid, 0, "system_status", "系统状态", "停止")
        
        # 添加控制板灯光显示
        light_label = QLabel("控制板灯光:")
        light_label.setMinimumWidth(80)
        light_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        params_grid.addWidget(light_label, 1, 0)
        
        # 创建灯光指示器(圆角矩形)
        self.light_indicator = QPushButton()
        self.light_indicator.setEnabled(False)  # 禁用点击功能，仅用于显示
        self.light_indicator.setFixedSize(30, 24)  # 设置为矩形，较小尺寸
        self.light_indicator.setStyleSheet("""
            QPushButton {
                border-radius: 5px;  /* 圆角矩形 */
                border: 1px solid #999;
                background-color: #f5f5f5;  /* 默认灰色 */
            }
        """)
        params_grid.addWidget(self.light_indicator, 1, 1)
        
        # 添加其他运行参数显示 (注意索引从2开始)
        self._add_param_row(params_grid, 2, "motor_speed", "电机转速", "0 RPM")
        self._add_param_row(params_grid, 3, "voltage", "电压值", "0 V")
        self._add_param_row(params_grid, 4, "temperature", "温度值", "0 °C")
        self._add_param_row(params_grid, 5, "power", "输出功率", "0 W")
        
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
        display_layout.addStretch()  # 添加弹性空间
   
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
        self.speed_input.setSuffix("   RPM")
        self.speed_input.setValue(600)
        self.speed_input.setStyleSheet("""
            QSpinBox {
                font-size: 14px;
                padding: 2px;
                min-height: 25px;
            }
            QSpinBox::up-button, QSpinBox::down-button {
                width: 16px;  /* 设置按钮宽度 */
            }
            QSpinBox::up-button:hover, QSpinBox::down-button:hover {
                background-color: #e6e6e6;
            }
            QSpinBox::up-button:pressed, QSpinBox::down-button:pressed {
                background-color: #d0d0d0;
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
        
         # 添加获取软件版本区域
        version_layout = QHBoxLayout()
       
        # 获取软件版本按钮
        self.get_version_button = QPushButton("获取软件版本")
        self.get_version_button.clicked.connect(self._on_get_version)
        self.get_version_button.setStyleSheet("""
            QPushButton {
                background-color: #9b59b6;
                color: white;
                border-radius: 5px;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #8e44ad;
            }
            QPushButton:pressed {
                background-color: #6c3483;
            }
        """)
        self.get_version_button.setFixedWidth(120)  # 固定按钮宽度
        
        
        # 版本信息显示标签
        self.version_label = QLabel("未获取")
        self.version_label.setMinimumWidth(150)  # 增加最小宽度
        self.version_label.setStyleSheet("""
            QLabel {
                color: #34495e;
                font-weight: bold;
                background-color: #f5f5f5;
                border: none;
                border-radius: 3px;
                padding: 5px 10px;
                text-align: center;
            }
        """)
        self.version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.version_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        
        version_layout.addWidget(self.get_version_button)
        version_layout.addWidget(self.version_label, 1)  # 添加伸缩因子1

        # 添加到控制布局
        control_layout.addLayout(version_layout)

        # 添加弹性空间在按钮下方
        control_layout.addStretch()
        
        self.main_layout.addWidget(control_frame, 1)
        
        
    def _on_refresh_status(self):
        """发送读取状态命令，获取电机即时状态"""
        # 检查串口是否打开
        if not self._check_serial_connection():
            return

         # 清理旧的信号连接
        try:
            self.serial_controller.data_received.disconnect()
        except:
            pass

        # 记录当前步骤
        self.current_step = 0
        self.command_steps = [
            {
                'command': "10 02 21 00 00 33 10 03",
                'handler': self._handle_status_response,
                'description': '读取状态'
            }   
        ]
        
        # 连接通用响应处理函数
        print(f"正在发送: {self.command_steps[0]['description']}")
        self.serial_controller.data_received.connect(self._universal_response_handler)
        
        # 发送第一个命令
        self.serial_controller.send_command(self.command_steps[0]['command'])
        
        # 设置超时处理
        self.response_timer = QTimer(self)
        self.response_timer.setSingleShot(True)
        self.response_timer.timeout.connect(self._on_response_timeout)
        self.response_timer.start(100)  # 100毫秒超时



    def _on_get_version(self):
        """获取软件版本"""
        if not self._check_serial_connection():
            return

         # 清理旧的信号连接
        try:
            self.serial_controller.data_received.disconnect()
        except:
            pass

        # 记录当前步骤
        self.current_step = 0
        self.command_steps = [
            {
                'command': "10 02 20 00 00 32 10 03",
                'handler': self._handle_version_response,
                'description': '获取软件版本'
            }   
        ]
        
        # 连接通用响应处理函数
        print(f"正在发送: {self.command_steps[0]['description']}")
        self.serial_controller.data_received.connect(self._universal_response_handler)
        
        # 发送第一个命令
        self.serial_controller.send_command(self.command_steps[0]['command'])
        
        # 设置超时处理
        self.response_timer = QTimer(self)
        self.response_timer.setSingleShot(True)
        self.response_timer.timeout.connect(self._on_response_timeout)
        self.response_timer.start(100)  # 100毫秒超时




    def _on_stop(self):
        """停止电机"""
        if not self._check_serial_connection():
            return
        
        # 清理旧的信号连接
        try:
            self.serial_controller.data_received.disconnect()
        except:
            pass

        # 记录当前步骤
        self.current_step = 0
        self.command_steps = [
            {
                'command': "10 02 80 00 00 92 10 03",
                'handler': self._handle_stop_response,
                'description': '电机停止'
            },
            {
                'command': "10 02 21 00 00 33 10 03",
                'handler': self._handle_status_response,
                'description': '读取状态'
            }
        ]
        
        # 连接通用响应处理函数
        print(f"正在发送: {self.command_steps[0]['description']}")
        self.serial_controller.data_received.connect(self._universal_response_handler)
        
        # 发送第一个命令
        self.serial_controller.send_command(self.command_steps[0]['command'])
        
        # 设置超时处理
        self.response_timer = QTimer(self)
        self.response_timer.setSingleShot(True)
        self.response_timer.timeout.connect(self._on_response_timeout)
        self.response_timer.start(100)  # 100毫秒超时


        # self.serial_controller.send_command(command)
        
        # self.serial_controller.data_received.connect(self._universal_response_handler)


        # 连接信号处理器用于启动响应
        # self.serial_controller.data_received.connect(self.handle_stop_response)

        # 发送读取状态命令获取最新状态
        # self._on_refresh_status()

    # def handle_stop_response(self, data):
    #     # 确认停止命令成功
    #     if len(data) >= 4 and data[2] == 0x80:
    #         # 处理停止成功
    #         print("电机停止命令已确认")
    #     # 断开此信号连接
    #     self.serial_controller.data_received.disconnect(self.handle_stop_response)
        
       

    def _on_start(self):
        """启动电机 - 问题修复版"""
        if not self._check_serial_connection():
            return
        
        # 清理旧的信号连接
        try:
            self.serial_controller.data_received.disconnect()
        except:
            pass
        
        # 记录当前步骤
        self.current_step = 0
        self.command_steps = [
            {
                'command': self.get_send_speed_command(self.speed_input.value()),
                'handler': self._handle_speed_response,
                'description': '设置速度'
            },
            {
                'command': "10 02 81 00 00 93 10 03", 
                'handler': self._handle_start_response,
                'description': '启动电机'
            },
            {
                'command': "10 02 21 00 00 33 10 03",
                'handler': self._handle_status_response,
                'description': '读取状态'
            }
        ]
        
        # 连接通用响应处理函数
        print(f"正在发送: {self.command_steps[0]['description']}")
        self.serial_controller.data_received.connect(self._universal_response_handler)
        
        # 发送第一个命令
        self.serial_controller.send_command(self.command_steps[0]['command'])
        
        # 设置超时处理
        self.response_timer = QTimer(self)
        self.response_timer.setSingleShot(True)
        self.response_timer.timeout.connect(self._on_response_timeout)
        self.response_timer.start(100)  # 100毫秒超时


    def _on_send_speed(self):
        """发送速度设定值"""
        if not self._check_serial_connection():
            return
            
        speed = self.speed_input.value()
        
        # 清理旧的信号连接
        try:
            self.serial_controller.data_received.disconnect()
        except:
            pass
        
        # 记录当前步骤
        self.current_step = 0
        self.command_steps = [
            {
                'command': self.get_send_speed_command(speed),
                'handler': self._handle_speed_response,
                'description': '设置速度'
            },
            {
                'command': "10 02 21 00 00 33 10 03",
                'handler': self._handle_status_response,
                'description': '读取状态'
            }
        ]
        
        # 连接通用响应处理函数
        print(f"正在发送: {self.command_steps[0]['description']}")
        self.serial_controller.data_received.connect(self._universal_response_handler)
        
        # 发送第一个命令
        self.serial_controller.send_command(self.command_steps[0]['command'])
        
        # 设置超时处理
        self.response_timer = QTimer(self)
        self.response_timer.setSingleShot(True)
        self.response_timer.timeout.connect(self._on_response_timeout)
        self.response_timer.start(100)  # 100毫秒超时




    def _universal_response_handler(self, data):
        """通用响应处理函数"""
        print(f"收到数据: {' '.join([f'{b:02X}' for b in data])}")
        self.serial_data_controller.record_received_data(data)

        if self.current_step < len(self.command_steps):
            # 调用当前步骤的处理函数
            self.command_steps[self.current_step]['handler'](data)
            
            # 停止当前超时计时器
            self.response_timer.stop()
            
            # 移至下一步
            self.current_step += 1
            if self.current_step < len(self.command_steps):
                # 发送下一个命令
                print(f"正在发送: {self.command_steps[self.current_step]['description']}")
                self.serial_controller.send_command(self.command_steps[self.current_step]['command'])
                
                # 重启超时计时器
                self.response_timer.start(1000)
            else:
                # 完成所有步骤，断开信号连接
                self.serial_controller.data_received.disconnect(self._universal_response_handler)
                print("完成所有命令序列")

    def _on_response_timeout(self):
        """响应超时处理 - 修复版"""
        print(f"命令 '{self.command_steps[self.current_step]['description']}' 响应超时")
        
        # 移至下一步
        self.current_step += 1
        if self.current_step < len(self.command_steps):
            # 发送下一个命令
            print(f"正在发送: {self.command_steps[self.current_step]['description']}")
            self.serial_controller.send_command(self.command_steps[self.current_step]['command'])
            
            # 重启超时计时器
            self.response_timer.start(1000)
        else:
            # 完成所有步骤，断开信号连接
            self.serial_controller.data_received.disconnect(self._universal_response_handler)
            print("超时后完成所有命令序列")

   

    def send_next_command(self):
        """发送队列中的下一个命令"""
        if not self.command_queue:
            return  # 队列为空，结束
            
        command_info = self.command_queue.pop(0)  # 取出队列首个元素
        
        # 断开之前的所有连接
        try:
            self.serial_controller.data_received.disconnect()
        except:
            pass
            
        # 连接新的响应处理函数
        self.serial_controller.data_received.connect(command_info['handler'])
        
        # 打印调试信息
        print(f"正在发送: {command_info['description']}")
        
        # 发送命令
        self.serial_controller.send_command(command_info['command'])
        
        # 设置超时处理
        self.response_timer = QTimer()
        self.response_timer.setSingleShot(True)
        self.response_timer.timeout.connect(self.handle_response_timeout)
        self.response_timer.start(100)  # 100毫秒超时

    def handle_response_timeout(self):
        """处理响应超时"""
        print("命令响应超时，继续下一个")
        self.send_next_command()  # 继续处理队列中的下一个命令

    def _handle_version_response(self, data):
        """处理版本信息响应"""
        if len(data) >= 4 and data[2] == 0x20:
            software_version_bytes = data[3:-3]  # Excluding header, cmd, checksum and footer
            software_version_str = ''.join([chr(b) for b in software_version_bytes])
            self.version_label.setText(software_version_str)
            print(f"软件版本: {software_version_str}")

        # 停止超时计时器
        self.response_timer.stop()

    # 各个命令的响应处理函数
    def _handle_speed_response(self, data):
        """处理速度设置响应"""
        if len(data) >= 4 and data[2] == 0x82:
            print("速度设置成功")
        
        # 停止超时计时器
        self.response_timer.stop()
        

    def _handle_start_response(self, data):
        """处理启动命令响应"""
        if len(data) >= 4 and data[2] == 0x81:
            print("电机启动成功")
        
        # 停止超时计时器
        self.response_timer.stop()
        

    def _handle_stop_response(self, data):
        """处理启动命令响应"""
        if len(data) >= 4 and data[2] == 0x80:
            print("电机停止成功")
        
        # 停止超时计时器
        self.response_timer.stop()
        

    def _handle_status_response(self, data):
        """处理状态查询响应"""
        if len(data) >= 13 and data[2] == 0x21:
            self.update_motor_info(data)
            print("状态查询完成")
        
        # 停止超时计时器
        self.response_timer.stop()
        
        # 不要尝试断开这个方法 - 它没有被直接连接



    def get_send_speed_command(self, speed):
        if (speed < 600 or speed > 3450):
            raise ValueError("速度值超出范围 (600-3450 RPM)")
        # 将速度值转为两个字节
        speed_high = (speed >> 8) & 0xFF
        speed_low = speed & 0xFF
        
        # 发送设置速度命令
        command = f"10 02 82 {speed_high:02X} {speed_low:02X} {(0x94 + speed_high + speed_low) & 0xFF:02X} 10 03"
        
        return command





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
                self.set_light_status('red')  # 红灯表示停止
            elif status == 0x0B:
                status_text = "运行"
                self.set_light_status('green')  # 绿灯表示运行
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
                                
                status_text = "故障"
                # 获取具体错误描述
                if status in fault_codes:
                    status_text = f"故障: {fault_codes[status]}"
                else:
                    status_text = "故障: 未定义错误"
                
                
                self.set_light_status('blue')  # 蓝灯表示故障
            
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

    def set_light_status(self, color):
        """设置灯光状态
        color: 'red', 'green', 'blue' 或 'gray'
        """
        style_base = """
            QPushButton {
                border-radius: 5px;
                border: 1px solid %s;
                background-color: %s;
            }
        """
        
        if color == 'red':
            self.light_indicator.setStyleSheet(style_base % ('#d32f2f', '#f44336'))
        elif color == 'green':
            self.light_indicator.setStyleSheet(style_base % ('#388e3c', '#4caf50'))
        elif color == 'blue':
            self.light_indicator.setStyleSheet(style_base % ('#1565c0', '#2196f3'))
        else:  # 默认灰色
            self.light_indicator.setStyleSheet(style_base % ('#999', '#f5f5f5'))

    def _debug_connections(self):
        """打印当前信号连接状态"""
        # 在 PyQt 中没有直接方法检查信号连接，但可以尝试断开再连接
        try:
            self.serial_controller.data_received.disconnect(self._universal_response_handler)
            print("_universal_response_handler 已连接")
            # 重新连接
            self.serial_controller.data_received.connect(self._universal_response_handler)
        except:
            print("_universal_response_handler 未连接")
            
        for handler_name in ["_handle_speed_response", "_handle_start_response", "_handle_status_response"]:
            handler = getattr(self, handler_name)
            try:
                self.serial_controller.data_received.disconnect(handler)
                print(f"{handler_name} 已连接")
                # 不要重新连接，因为我们只是在调试
            except:
                print(f"{handler_name} 未连接")