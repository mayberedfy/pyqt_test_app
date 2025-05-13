from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QComboBox, QLineEdit, QPushButton, QTextEdit, QGroupBox, QGridLayout)
from PyQt6 import QtCore
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6 import QtGui
from controllers.serial_controller import SerialController
import serial
import serial.tools.list_ports
from datetime import datetime

class SerialWidget(QWidget):

    data_received = QtCore.pyqtSignal(str) 

    def __init__(self, serial_controller=None, motor_widget=None, control_widget=None, parent_type=None, parent=None):
        super().__init__(parent)
    
        # 使用传入的串口控制器或创建新的
        self.serial_controller = serial_controller 
        self.motor_widget = motor_widget
        self.control_widget = control_widget

        self.parent_type = parent_type  # "control" 或 "motor"
        self.command_handlers = {}


        print(f"SerialWidget parent_type: {self.parent_type}")
        print(f"command_handlers: {self.command_handlers}")

        # 初始化串口对象
        self.serial = None
        self.is_open = False  # 添加状态追踪

        self._create_ui()

        self.data_received.connect(self.update_display)
        
        # 初始化可用串口列表
        self.refresh_ports()

        # 连接串口控制器的信号
        self.serial_controller.data_received.connect(self.handle_data_received)
        self.serial_controller.command_sent.connect(self.handle_command_sent)  # 连接新信号

    def _create_ui(self):
        """创建用户界面 - 左右布局版本"""
        # 创建主布局
        main_layout = QHBoxLayout(self)  # 使用水平布局作为主布局
        main_layout.setContentsMargins(10, 40, 10, 10)
        main_layout.setSpacing(10)
        
        # ===== 左侧：控制面板 =====
        left_panel = QVBoxLayout()
        left_panel.setSpacing(10)
        
        # 串口设置组
        port_group = QGroupBox("串口设置")
        port_layout = QVBoxLayout(port_group)
        port_layout.setContentsMargins(8, 8, 8, 8)
        port_layout.setSpacing(8)
        
        # 端口设置
        port_row = QHBoxLayout()
        port_label = QLabel("端口:")
        port_label.setFixedWidth(40)
        self.input_port_name = QComboBox()
        self.input_port_name.setEditable(True)
        port_row.addWidget(port_label)
        port_row.addWidget(self.input_port_name)
        port_layout.addLayout(port_row)
        
        # 波特率设置
        baud_row = QHBoxLayout()
        baud_label = QLabel("波特率:")
        baud_label.setFixedWidth(40)
        self.input_baud_rate = QComboBox()
        self.input_baud_rate.addItems(["300", "600", "1200", "2400", "4800", "9600", "19200", "38400", "57600", "115200"])
        self.input_baud_rate.setCurrentText("9600")
        baud_row.addWidget(baud_label)
        baud_row.addWidget(self.input_baud_rate)
        port_layout.addLayout(baud_row)
        
        # 控制按钮区域 - 三个按钮从上到下排列
        buttons_layout = QVBoxLayout()
        buttons_layout.setSpacing(8)
        
        # 刷新端口按钮 (第一个按钮)
        self.btn_refresh = QPushButton("刷新端口")
        self.btn_refresh.setFixedHeight(36)
        self.btn_refresh.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border-radius: 4px;
                border: none;
                padding: 6px 12px;
            }
            QPushButton:hover {
                background-color: #0b7dda;
            }
        """)
        buttons_layout.addWidget(self.btn_refresh)
        
        # Open/Close 按钮 (第二个按钮) - 更新样式定义
        self.btn_toggle = QPushButton("打开")  # 改为中文"打开"
        self.btn_toggle.setFixedHeight(36)
        self.btn_toggle.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        # 不设置默认样式，通过updateToggleButtonStyle方法动态设置
        buttons_layout.addWidget(self.btn_toggle)
        
        # 清空显示按钮 (第三个按钮)
        self.btn_clear = QPushButton("清空显示")
        self.btn_clear.setFixedHeight(36)
        self.btn_clear.setStyleSheet("""
            QPushButton {
                background-color: #ff5722;
                color: white;
                border-radius: 4px;
                border: none;
                padding: 6px 12px;
            }
            QPushButton:hover {
                background-color: #e64a19;
            }
            QPushButton:pressed {
                background-color: #bf360c;
            }
            QPushButton:disabled {
                background-color: #ffccbc;
                color: #b0bec5;
            }
        """)
        self.btn_clear.setEnabled(False)  # 初始状态设为禁用
        buttons_layout.addWidget(self.btn_clear)
        
        port_layout.addLayout(buttons_layout)
        port_layout.addStretch()  # 添加弹性空间
        
        # 添加端口设置到左侧面板
        left_panel.addWidget(port_group)
        left_panel.addStretch()  # 添加弹性空间推动组件向上
        
        # ===== 右侧：数据显示面板 =====
        right_panel = QVBoxLayout()
        
        data_group = QGroupBox("数据显示")
        data_layout = QVBoxLayout(data_group)
        data_layout.setContentsMargins(8, 8, 8, 8)
        
        # 文本显示区
        self.data_display = QTextEdit()
        self.data_display.setReadOnly(True)
        self.data_display.setStyleSheet("""
            QTextEdit {
                background-color: #f8f8f8;
                border: 1px solid #ddd;
                border-radius: 4px;
                font-family: Consolas, Monaco, monospace;
                font-size: 9pt;
            }
        """)
        data_layout.addWidget(self.data_display)
        
        # 添加数据显示到右侧面板
        right_panel.addWidget(data_group)
        
        # 添加左右两个面板到主布局，设置比例为1:2
        main_layout.addLayout(left_panel, 1)
        main_layout.addLayout(right_panel, 2)
        
        # 连接事件处理器
        self.btn_toggle.clicked.connect(self.toggle_serial)
        self.btn_refresh.clicked.connect(self.refresh_ports)
        self.btn_clear.clicked.connect(self.clear_display)
        
        # 初始化按钮样式
        self.updateToggleButtonStyle()

    def register_command_handler(self, cmd, handler):
        """注册特定命令处理函数"""
        self.command_handlers[cmd] = handler

    def refresh_ports(self):
        """List available serial ports and add them to the combo box"""
        self.input_port_name.clear()  # Clear existing items
        ports = serial.tools.list_ports.comports()
        for port in ports:
            self.input_port_name.addItem(port.device)
            print(f"Found port: {port.device} - {port.description}")
        
        # Select the first port if available
        if self.input_port_name.count() > 0:
            self.input_port_name.setCurrentIndex(0)
        else:
            print("No serial ports found")


    def toggle_serial(self):
        """切换串口开启/关闭状态"""
        if not self.is_open:
            try:
                # 获取当前选择的串口和波特率
                port = self.input_port_name.currentText()
                baud_rate = int(self.input_baud_rate.currentText())
                
                # 打开串口通信
                self.serial_controller.open_port(port, baud_rate)

                # 检查串口是否成功打开
                if self.serial_controller.running is True:                        
                    # 更新按钮状态和文本
                    self.is_open = True
                    self.updateToggleButtonStyle()  # 更新按钮样式
                    self.input_port_name.setEnabled(False)
                    self.input_baud_rate.setEnabled(False)

                    # 在显示框中添加状态信息
                    self.data_display.append(f"串口已打开: {port}, {baud_rate}波特率")
                    self.btn_clear.setEnabled(True)  # 有数据时启用清空按钮
                
                else:
                    self.data_display.append(f"串口打开失败: {port}")
                    self.btn_clear.setEnabled(True)  # 有数据时启用清空按钮
                    return
                    
            except Exception as e:
                self.data_display.append(f"打开串口失败: {str(e)}")
                self.btn_clear.setEnabled(True)  # 有数据时启用清空按钮
                return
        else:
            try:
                # 关闭串口
                if self.serial_controller.running is True:                        
                    self.serial_controller.close_port()
                self.is_open = False
                
                # 更新按钮样式和状态
                self.updateToggleButtonStyle()  # 更新按钮样式
                self.input_port_name.setEnabled(True)
                self.input_baud_rate.setEnabled(True)
                
                # 在显示框中添加状态信息
                self.data_display.append("串口已关闭")
                self.btn_clear.setEnabled(True)  # 有数据时启用清空按钮
                
            except Exception as e:
                self.data_display.append(f"关闭串口失败: {str(e)}")
                self.btn_clear.setEnabled(True)  # 有数据时启用清空按钮
                return

        # 在串口状态改变后（打开或关闭）
        if self.control_widget and hasattr(self.control_widget, 'update_lights_clickable_state'):
            self.control_widget.update_lights_clickable_state()

    def clear_display(self):
        """清空显示框内容"""
        self.data_display.clear()
        self.btn_clear.setEnabled(False)  # 清空后禁用按钮

    def update_display(self, data):
        """更新显示内容并启用清空按钮"""
        self.data_display.append(data)
        self.data_display.moveCursor(QtGui.QTextCursor.MoveOperation.End)
        self.btn_clear.setEnabled(True)  # 有新数据时启用清空按钮

    def handle_data_received(self, data):
        if self.parent_type == "control":
            self.control_serial_data_handle(data)
        elif self.parent_type == "motor":
            self.motor_serial_data_handle(data)
        
    def handle_command_sent(self, command):
        """处理发送的命令"""
        # 格式化并显示命令
        display_text = self.format_command(command)
        self.update_display(display_text)


    # 控制板的串口数据处理方法
    def control_serial_data_handle(self, data):
        try:
            
            # 转换数据为十六进制
            hex_data = ' '.join([f"{byte:02X}" for byte in data])
            self.record_received_data(data)

            data_length = len(data)
            if data_length < 8:
                print("Received data is too short:", hex_data)
                return

            # 通用处理...
            CMD = data[2]
            # 处理数据
            # 先校验尾数
            response = ""
            if data[0] == 0x10 and data[1] == 0x02 :
                CMD = data[2]
                if CMD == 0x83:
                    # 读取档位命令：
                    # 发送：CMD = 0x83  DATA0 = 速度档位信息 DATA1 = 时间档位信息
                    # 读系统参数：
                    # 发送：CMD = 0x83  DATA0 = 0 	DATA1 = 0
                    # 应答：格式同发送 
                    # 发送：CMD = 0x83  DATA0 = 速度档位信息 DATA1 = 时间档位信息;
                    response = "10 02 83 00 01 96 10 03"
                    # 调整档位信息
                    speed_gear = data[3]
                    time_gear = data[4]

                    self.control_widget.speed_knob.setValue(speed_gear)
                    self.control_widget.time_knob.setValue(time_gear)
                    self.control_widget.update_knob_label(self.control_widget.speed_knob, self.control_widget.speed_knob_label)
                    self.control_widget.update_knob_label(self.control_widget.time_knob, self.control_widget.time_knob_label)
                    print(f"Speed Gear: {speed_gear}, Time Gear: {time_gear}")
                                   
                elif CMD == 0x82:
                    # 设定转速
                    # 发送：CMD = 0x82  DATA0 ~DATA1：设定转速值
                    # 发送：CMD = 0x82  DATA0 ~DATA1：设定转速值
                    # 应答：格式同发送  DATA0 = 0  DATA1 = ACK
                    response = "10 02 82 00 01 95 10 03"
                    
                elif CMD == 0x81:   
                    # 电机运行
                    # 发送：CMD = 0x81  DATA0 = 0 	DATA1 = 0
                    # 应答：格式同发送  DATA0 = 0  DATA1 = ACK
                    response = "10 02 81 00 01 94 10 03"

                elif CMD == 0x80:
                    # 电机停止
                    # 发送：CMD = 0x80  DATA0 = 0 	DATA1 = 0
                    # 应答：格式同发送  DATA0 = 0  DATA1 = ACK
                    response = "10 02 80 00 01 93 10 03"

                elif CMD == 0x21:
                    # 处理命令5# 读系统参数：
                    # 发送：CMD = 0x21  DATA0 = 0 	DATA1 = 0
                    # 应答：格式同发送
                    # DATA0：系统状态
                    # DATA1~DATA2：电机转速值
                    # DATA3~DATA4：电压值
                    # DATA5：IPM温度值
                    # DATA6~DATA7：输出功率值 
                    response = "10 02 21 23 00 00 00 37 1C 00 00 A9 10 03"
                    status = data[3]

                    light_color = ""
                    system_status = ""
                    if status == 0x00:
                        light_color = "red"
                        system_status = "停止"
                    elif status == 0x20 or status == 0x21 or status == 0x22 or status == 0x23 or status == 0x24 or status == 0x25 or status == 0x26 or status == 0x27 or status == 0x28 or status == 0x29 or status == 0x2A or status == 0x2B or status == 0x50:
                        light_color = "blue"
                        system_status = "故障"
                    elif status == 0x0B:
                        light_color = "green"
                        system_status = "运行"
                    else:
                        print(f"Unknown status: {status}")

                    print(f"System Status: {system_status}, Light Color: {light_color}")

                    # self.control_widget.toggle_light(light_color)
                    

                elif CMD == 0x20:
                    # 读取软件版本：
                    # 发送：CMD = 0x20  DATA0 = 0 	DATA1 = 0
                    # 应答：格式同发送
                    # DATA0 ~DATAn：版本信息(ASCII码)
                    response = "10 02 20 56 44 32 2E 30 2E 30 BA 10 03"
                    
            else:
                print("Received invalid data:", hex_data)


            # 测试控制板时，需要将应答数据发送到串口
            self.serial_controller.send_command(response)

            # timestamp01 = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
            # formatted_data01 = f"[{timestamp01}] Ack: {response}"
            # print(formatted_data01)
            # self.data_display.append(formatted_data01)
                

        except Exception as e:
            print(f"Error processing received data: {e}")
            import traceback
            traceback.print_exc()




    def motor_serial_data_handle(self, data):
        try:

            # 转换数据为十六进制
            hex_data = ' '.join([f"{byte:02X}" for byte in data])

            self.record_received_data(data)

            data_length = len(data)
        
            CMD = data[2]
            # 处理数据
            # 先校验尾数
            response = ""

            if data[0] == 0x10 and data[1] == 0x02 :
                CMD = data[2]
                if CMD == 0x83:
                    # 读取档位命令：
                    # 发送：CMD = 0x83  DATA0 = 速度档位信息 DATA1 = 时间档位信息
                    # 读系统参数：
                    # 发送：CMD = 0x83  DATA0 = 0 	DATA1 = 0
                    # 应答：格式同发送 
                    # 发送：CMD = 0x83  DATA0 = 速度档位信息 DATA1 = 时间档位信息;
                    response = "10 02 83 00 01 96 10 03"

                                   
                elif CMD == 0x82:
                    # 设定转速
                    # 发送：CMD = 0x82  DATA0 ~DATA1：设定转速值
                    # 应答：格式同发送  DATA0 = 0  DATA1 = ACK
                    response = "10 02 82 00 01 95 10 03"

                elif CMD == 0x81:
                    # 电机运行
                    # 发送：CMD = 0x81  DATA0 = 0 	DATA1 = 0
                    # 应答：格式同发送  DATA0 = 0  DATA1 = ACK
                    response = "10 02 81 00 01 94 10 03"

                elif CMD == 0x80:
                    # 电机停止
                    # 发送：CMD = 0x80  DATA0 = 0 	DATA1 = 0
                    # 应答：格式同发送  DATA0 = 0  DATA1 = ACK
                    response = "10 02 80 00 01 93 10 03"

                elif CMD == 0x21:
                    # 处理命令5# 读系统参数：
                    # 发送：CMD = 0x21  DATA0 = 0 	DATA1 = 0
                    # 应答：格式同发送
                    # DATA0：系统状态
                    # DATA1~DATA2：电机转速值
                    # DATA3~DATA4：电压值
                    # DATA5：IPM温度值
                    # DATA6~DATA7：输出功率值 
                    response = "10 02 21 23 00 00 00 37 1C 00 00 A9 10 03"
                    status = data[3]

                    light_color = ""
                    system_status = ""
                    if status == 0x00:
                        light_color = "red"
                        system_status = "停止"
                    elif status == 0x20 or status == 0x21 or status == 0x22 or status == 0x23 or status == 0x24 or status == 0x25 or status == 0x26 or status == 0x27 or status == 0x28 or status == 0x29 or status == 0x2A or status == 0x2B or status == 0x50:
                        light_color = "blue"
                        system_status = "故障"
                    elif status == 0x0B:
                        light_color = "green"
                        system_status = "运行"
                    else:
                        print(f"Unknown status: {status}")

                    print(f"System Status: {system_status}, Light Color: {light_color}")

                    print("data_length:", data_length)
                    if data_length < 10:
                        # 电机停止
                        system_status = "停止"
                        light_color = "red"
                        self.motor_widget.system_status_label.setText(system_status)
                        self.motor_widget.motor_speed_label.setText("0 RPM")
                        self.motor_widget.voltage_label.setText("0 V")
                        self.motor_widget.temperature_label.setText("0 °C")
                        self.motor_widget.power_label.setText("0 W")

                    else:
                        motor_speed = (data[4] << 8) | data[5]
                        voltage = (data[6] << 8) | data[7]
                        temperature = data[8]
                        power = (data[9] << 8) | data[10]
                        # Convert motor speed from raw value to decimal
                        motor_speed = (data[4] << 8) | data[5]  # Combine high byte and low byte
                        motor_speed_actual = motor_speed / 10.0  # Assuming a scaling factor of 10
                        # Convert voltage from raw value to actual volts (scaling factor depends on hardware)
                        voltage_actual = voltage / 10.0  # Assuming a scaling factor of 10
                        temperature_actual = temperature / 10.0  # Assuming temperature is already in °C
                        power_actual = power / 10.0
                        self.motor_widget.system_status_label.setText(system_status)
                        self.motor_widget.motor_speed_label.setText(f"{motor_speed_actual} RPM")
                        self.motor_widget.voltage_label.setText(f"{voltage_actual}")
                        self.motor_widget.temperature_label.setText(f"{temperature_actual} °C")
                        self.motor_widget.power_label.setText(f"{power_actual} W")
                    

                elif CMD == 0x20:
                    # 读取软件版本：
                    # 发送：CMD = 0x20  DATA0 = 0 	DATA1 = 0
                    # 应答：格式同发送
                    # DATA0 ~DATAn：版本信息(ASCII码)
                    # response = "10 02 20 56 44 32 2E 30 2E 30 BA 10 03"
                    software_version = data[3:7]
                    software_version_str = ''.join([chr(b) for b in software_version])
                    print(f"Software Version: {software_version_str}")
                    # self.motor_widget.software_version_label.setText(software_version_str)
            else:
                print("Received invalid data:", hex_data)
                

        except Exception as e:
            print(f"Error processing received data: {e}")
            import traceback
            traceback.print_exc()





    def record_received_data(self, data):
        """记录接收到的数据"""
        try:
            # 获取当前时间戳
            timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
            
            # 转换数据为十六进制
            hex_data = ' '.join([f"{byte:02X}" for byte in data])
            # 组合时间戳和数据
            formatted_data = f"[{timestamp}] << {hex_data}"
            print(formatted_data)
            self.update_display(formatted_data)
        except Exception as e:
            print(f"Error recording received data: {e}")



    def format_command(self, command):
        """将命令格式化为易读形式"""

        # 获取当前时间戳
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]

        try:
            
            # 如果是字符串形式的十六进制命令
            if isinstance(command, str):
                # 去除空格，然后每两个字符插入一个空格
                cmd = command.replace(" ", "")
                cmd = " ".join([cmd[i:i+2] for i in range(0, len(cmd), 2)])
                print(f"[{timestamp}] >> {cmd}")
                return f"[{timestamp}] >> {cmd}"
            # 如果是字节数组
            else:
                # 转换为十六进制字符串
                hex_str = " ".join([f"{b:02X}" for b in command])
                print(f"[{timestamp}] >> {hex_str}")
                return f"[{timestamp}] >> {hex_str}"
        except:
            # 如果格式化失败，直接返回原始命令
            return f"[{timestamp}] >> {command}"

    def updateToggleButtonStyle(self):
        """根据串口连接状态更新按钮样式"""
        if not self.is_open:
            # 未连接状态 - 绿色，显示"打开"
            self.btn_toggle.setText("打开")
            self.btn_toggle.setStyleSheet("""
                QPushButton {
                    background-color: #4CAF50;
                    color: white;
                    border-radius: 4px;
                    border: none;
                    padding: 6px 12px;
                }
                QPushButton:hover {
                    background-color: #45a049;
                }
                QPushButton:pressed {
                    background-color: #3d8b40;
                }
            """)
        else:
            # 已连接状态 - 红色，显示"关闭"
            self.btn_toggle.setText("关闭")
            self.btn_toggle.setStyleSheet("""
                QPushButton {
                    background-color: #f44336;
                    color: white;
                    border-radius: 4px;
                    border: none;
                    padding: 6px 12px;
                }
                QPushButton:hover {
                    background-color: #d32f2f;
                }
                QPushButton:pressed {
                    background-color: #b71c1c;
                }
            """)
