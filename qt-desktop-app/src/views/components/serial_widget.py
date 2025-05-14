from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QComboBox, QLineEdit, QPushButton, QTextEdit, QGroupBox, QGridLayout, QFileDialog,
                            QApplication)
from PyQt6 import QtCore
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6 import QtGui
from controllers.serial_data_controller import SerialDataController
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

        # 创建新的串口控制器实例
        self.serial_data_controller = SerialDataController(
            self.serial_controller,
            self.control_widget,
            self.motor_widget,
            self
        )  

        # "control" 或 "motor"
        self.parent_type = parent_type
        self.command_handlers = {}

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
        main_layout.setContentsMargins(10, 1, 10, 10)
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
        
        # 刷新端口按钮 (第一个按钮) - 修改风格，移除背景色，添加图标
        refresh_button_layout = QHBoxLayout()
        self.btn_refresh = QPushButton("刷新端口⟳")
        self.btn_refresh.setFixedHeight(36)
        self.btn_refresh.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        
        # 设置刷新按钮样式 - 没有背景色，只有边框
        self.btn_refresh.setStyleSheet("""
            QPushButton {
                color: #2196F3;
                border: 1px solid #2196F3;
                border-radius: 4px;
                padding: 6px 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e3f2fd;
            }
            QPushButton:pressed {
                background-color: #bbdefb;
            }
        """)
        
        # 添加图标和按钮到同一行
        refresh_button_layout.addWidget(self.btn_refresh)
        buttons_layout.addLayout(refresh_button_layout)
        
        # Open/Close 按钮 (第二个按钮)
        self.btn_toggle = QPushButton("打开")
        self.btn_toggle.setFixedHeight(36)
        self.btn_toggle.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        # 样式会在updateToggleButtonStyle方法中设置
        buttons_layout.addWidget(self.btn_toggle)
        
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
        
        # 右侧按钮区域 - 放置清空显示、数据保存和数据复制按钮
        buttons_row = QHBoxLayout()
           
        # 数据保存按钮
        self.btn_save = QPushButton("数据保存")
        self.btn_save.setFixedHeight(36)
        self.btn_save.setStyleSheet("""
            QPushButton {
                color: #4caf50;
                border: 1px solid #4caf50;
                border-radius: 4px;
                padding: 6px 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e8f5e9;
            }
            QPushButton:pressed {
                background-color: #c8e6c9;
            }
            QPushButton:disabled {
                color: #c8e6c9;
                border: 1px solid #c8e6c9;
            }
        """)
        self.btn_save.setEnabled(False)
        buttons_row.addWidget(self.btn_save)
        
        # 数据复制按钮
        self.btn_copy = QPushButton("数据复制")
        self.btn_copy.setFixedHeight(36)
        self.btn_copy.setStyleSheet("""
            QPushButton {
                color: #3f51b5;
                border: 1px solid #3f51b5;
                border-radius: 4px;
                padding: 6px 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e8eaf6;
            }
            QPushButton:pressed {
                background-color: #c5cae9;
            }
            QPushButton:disabled {
                color: #c5cae9;
                border: 1px solid #c5cae9;
            }
        """)
        self.btn_copy.setEnabled(False)
        buttons_row.addWidget(self.btn_copy)

         # 清空显示按钮
        self.btn_clear = QPushButton("清空显示")
        self.btn_clear.setFixedHeight(36)
        self.btn_clear.setStyleSheet("""
            QPushButton {
                color: #ff5722;
                border: 1px solid #ff5722;
                border-radius: 4px;
                padding: 6px 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #fbe9e7;
            }
            QPushButton:pressed {
                background-color: #ffccbc;
            }
            QPushButton:disabled {
                color: #ffccbc;
                border: 1px solid #ffccbc;
            }
        """)
        self.btn_clear.setEnabled(False)
        buttons_row.addWidget(self.btn_clear)
        
        
        # 添加按钮行到布局
        data_layout.addLayout(buttons_row)
        
        # 添加数据显示到右侧面板
        right_panel.addWidget(data_group)
        
        # 添加左右两个面板到主布局，设置比例为1:2
        main_layout.addLayout(left_panel, 1)
        main_layout.addLayout(right_panel, 2)
        
        # 连接事件处理器
        self.btn_toggle.clicked.connect(self.toggle_serial)
        self.btn_refresh.clicked.connect(self.refresh_ports)
        self.btn_clear.clicked.connect(self.clear_display)
        self.btn_save.clicked.connect(self.save_display_data)
        self.btn_copy.clicked.connect(self.copy_display_data)
        
        # 初始化按钮样式
        self.updateToggleButtonStyle()

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
        self.btn_save.setEnabled(False)   # 清空后禁用按钮
        self.btn_copy.setEnabled(False)   # 清空后禁用按钮

    def update_display(self, data):
        """更新显示内容并启用清空按钮"""
        self.data_display.append(data)
        self.data_display.moveCursor(QtGui.QTextCursor.MoveOperation.End)
        self.btn_clear.setEnabled(True)  # 有新数据时启用清空按钮
        self.btn_save.setEnabled(True)   # 有新数据时启用保存按钮
        self.btn_copy.setEnabled(True)   # 有新数据时启用复制按钮

    def handle_data_received(self, data):
        if self.parent_type == "control":
            self.serial_data_controller.control_serial_data_handle(data)
        elif self.parent_type == "motor":
            self.serial_data_controller.motor_serial_data_handle(data)

    def handle_command_sent(self, command):
        """处理发送的命令"""
        # 格式化并显示命令
        display_text = self.format_command(command)
        self.update_display(display_text)




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

    def save_display_data(self):
        """保存显示框中的数据到文件"""
        # 获取显示框中的文本
        text = self.data_display.toPlainText()
        
        if not text:
            return
        
        # 打开文件保存对话框
        options = QFileDialog.Option.DontUseNativeDialog
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "保存数据",
            "",
            "文本文件 (*.txt);;所有文件 (*)",
            options=options
        )
        
        if file_path:
            # 确保文件有.txt扩展名
            if not file_path.endswith('.txt'):
                file_path += '.txt'
                
            try:
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(text)
                    
                # 显示保存成功消息
                self.data_display.append(f"\n[系统] 数据已保存到: {file_path}")
            except Exception as e:
                self.data_display.append(f"\n[错误] 保存失败: {str(e)}")

    def copy_display_data(self):
        """复制显示框中的数据到剪贴板"""
        # 获取显示框中的文本
        text = self.data_display.toPlainText()
        
        if not text:
            return
            
        # 复制到剪贴板
        clipboard = QApplication.clipboard()
        clipboard.setText(text)
        
        # 显示复制成功消息
        self.data_display.append("\n[系统] 数据已复制到剪贴板")
