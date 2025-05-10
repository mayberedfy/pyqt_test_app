from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QComboBox, QLineEdit, QPushButton, QTextEdit)
from PyQt6 import QtCore
from PyQt6.QtCore import Qt
from PyQt6 import QtGui
from controllers.serial_controller import SerialController
from controllers.serial_data_controller import SerialDataController
from views.components.control_widget import ControlWidget
import serial
import serial.tools.list_ports
from datetime import datetime

class SerialWidget(QWidget):

    data_received = QtCore.pyqtSignal(str) 

    def __init__(self, control_widget=None, parent=None):
        super().__init__(parent)
        self.control_widget = control_widget

        # 创建主水平布局，设置更小的边距和间距
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(10, 50, 10, 10)
        self.main_layout.setSpacing(10)  # 设置布局内部组件间距
        
        # 左侧控制区域，设置更小的间距
        left_layout = QVBoxLayout()
        left_layout.setSpacing(5)  # 减小垂直间距
        
        # 端口号行
        port_layout = QHBoxLayout()
        port_label = QLabel("端口号:", self)
        port_label.setFixedWidth(60)
        self.input_port_name = QComboBox(self)
        self.input_port_name.setFixedWidth(100)
        port_layout.addWidget(port_label)
        port_layout.addWidget(self.input_port_name)
        port_layout.addStretch()

        # 波特率行
        baud_layout = QHBoxLayout()
        baud_label = QLabel("波特率:", self)
        baud_label.setFixedWidth(60)
        self.input_baud_rate = QLineEdit(self)
        self.input_baud_rate.setPlaceholderText("Baud Rate")
        self.input_baud_rate.setFixedWidth(100)
        self.input_baud_rate.setText("9600")
        baud_layout.addWidget(baud_label)
        baud_layout.addWidget(self.input_baud_rate)
        baud_layout.addStretch()

        # 按钮布局
        button_layout = QVBoxLayout()
        self.btn_toggle = QPushButton("Open", self)
        self.btn_toggle.setFixedWidth(60)
        self.btn_clear = QPushButton("Clear", self)
        self.btn_clear.setFixedWidth(60)
        button_layout.addWidget(self.btn_toggle)
        button_layout.addWidget(self.btn_clear)
        button_layout.addStretch()

        # 将控件添加到左侧布局
        left_layout.addLayout(port_layout)
        left_layout.addLayout(baud_layout)
        left_layout.addLayout(button_layout)
        left_layout.addStretch()

        # 设置data_display的宽度、高度和边距
        self.data_display = QTextEdit(self)
        self.data_display.setReadOnly(True)
        self.data_display.setMinimumWidth(300)  # 设置最小宽度
        self.data_display.setMinimumHeight(300)  # 设置最小高度
        self.data_display.setContentsMargins(0, 0, 0, 0)  # 移除内部边距

        # 将左右两侧添加到主布局
        self.main_layout.addLayout(left_layout)
        self.main_layout.addWidget(self.data_display, 1)  # 添加拉伸因子1

        # 初始化串口对象
        self.serial = None
        self.is_open = False  # 添加状态追踪

        self.serial_controller = SerialController()
        self.serial_data_controller = SerialDataController()
        
        # 连接按钮信号
        self.btn_toggle.clicked.connect(self.toggle_serial)
        self.btn_clear.clicked.connect(self.clear_display)
        
        self.data_received.connect(self.update_display)
        
        # 初始化可用串口列表
        self.list_serial_ports()



    def update_ports(self):
        """更新可用串口列表"""
        self.input_port_name.clear()
        ports = [port.device for port in serial.tools.list_ports.comports()]
        self.input_port_name.addItems(ports)

    def list_serial_ports(self):
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
                baud_rate = int(self.input_baud_rate.text())
                
                # 打开串口通信
                self.serial_controller.open_port(port, baud_rate)

                # 检查串口是否成功打开
                if self.serial_controller.running is True:                        
                    # 更新按钮状态和文本
                    self.is_open = True
                    self.btn_toggle.setText("Close")
                    self.input_port_name.setEnabled(False)
                    self.input_baud_rate.setEnabled(False)

                    # 在显示框中添加状态信息
                    self.data_display.append(f"串口已打开: {port}, {baud_rate}波特率")
                
                else:
                    self.data_display.append(f"串口打开失败: {port}")
                    return
                    
                # 处理串口数据接收
                self.serial_controller.data_received.connect(self.handle_data_received)
                             
            except Exception as e:
                self.data_display.append(f"打开串口失败: {str(e)}")
                return
        else:
            try:
                # 关闭串口
                if self.serial_controller.running is True:                        
                    self.serial_controller.close_port()
                self.is_open = False
                
                # 更新按钮状态和文本
                self.btn_toggle.setText("Open")
                self.input_port_name.setEnabled(True)
                self.input_baud_rate.setEnabled(True)
                
                # 在显示框中添加状态信息
                self.data_display.append("串口已关闭")
                
            except Exception as e:
                self.data_display.append(f"关闭串口失败: {str(e)}")
                return

    def clear_display(self):
        """清空显示框内容"""
        self.data_display.clear()

    def update_display(self, data):
        self.data_display.append(data)
        self.data_display.moveCursor(QtGui.QTextCursor.MoveOperation.End)
        self.btn_clear.setEnabled(True)  # 有新数据时启用清空按钮

    def handle_data_received(self, data):
        self.control_serial_data_handle(data)
        

    def control_serial_data_handle(self, data):
        try:
            # 获取当前时间戳
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
            
            # 转换数据为十六进制
            hex_data = ' '.join([f"{byte:02X}" for byte in data])
            # 组合时间戳和数据
            formatted_data = f"[{timestamp}] Rec: {hex_data}"
            print(formatted_data)
            # self.data_received.emit(formatted_data)
            self.update_display(formatted_data)

            # 处理数据
            # 先校验尾数
            response = ""
            if data[0] == 0x10 and data[1] == 0x02:
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
                    print(f"Speed Gear: {speed_gear}, Time Gear: {time_gear}")
                    
                    
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
                    if status == 0x00:
                        # self.light_group.set_active_light(self.red_light)
                        light_color = "red"
                        self.control_widget.toggle_light(self.control_widget.red_light)
                    elif status == 0x20 or status == 0x21 or status == 0x22 or status == 0x23 or status == 0x24 or status == 0x25 or status == 0x26 or status == 0x27 or status == 0x28 or status == 0x29 or status == 0x2A or status == 0x2B or status == 0x50:    
                        # self.light_group.set_active_light(self.blue_light)  
                        light_color = "blue"
                        # self.control_widget.toggle_light(self.control_widget.blue_light)
                    elif status == 0x0B:
                        # self.light_group.set_active_light(self.green_light)  
                        light_color = "green"
                        # self.control_widget.toggle_light(self.control_widget.green_light, True)

                    else:
                        print(f"Unknown status: {status}")

                    print(f"Light Color: {light_color}")

                elif CMD == 0x20:
                    # 读取软件版本：
                    # 发送：CMD = 0x20  DATA0 = 0 	DATA1 = 0
                    # 应答：格式同发送
                    # DATA0 ~DATAn：版本信息(ASCII码)
                    response = "10 02 20 56 44 32 2E 30 2E 30 BA 10 03"
                    
            else:
                print("Received invalid data:", hex_data)

            self.serial_controller.send_command(response)

            timestamp01 = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
            formatted_data01 = f"[{timestamp01}] Ack: {response}"
            print(formatted_data01)
            self.data_display.append(formatted_data01)

        except Exception as e:
            print(f"Error processing received data: {e}")
            import traceback
            traceback.print_exc()



