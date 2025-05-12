from datetime import datetime
import serial
import threading
import time
from PyQt6.QtCore import QObject, pyqtSignal


class SerialController(QObject):
    data_received = pyqtSignal(bytes)  # 接受任何类型
    command_sent = pyqtSignal(bytes)  # 新增信号，用于通知命令已发送

    def __init__(self):
        super().__init__()
        self.serial_port = None
        self.running = False

    def open_port(self, port_name, baud_rate):
        try:
            self.serial_port = serial.Serial(
                port=port_name,
                baudrate=baud_rate,
                timeout=1,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE
            )
            self.running = True
            threading.Thread(target=self.read_data, daemon=True).start()
            print(f"Serial port {port_name} opened at {baud_rate} baud.")
        except serial.SerialException as e:
            print(f"Failed to open serial port: {e}")
            self.serial_port = None

    def close_port(self):
        self.running = False
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()
            print("Serial port closed.")

    def send_command(self, command):
        
        # if self.serial_port and self.serial_port.is_open:
        #     try:
        #         # 获取当前时间戳
        #         timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
                
        #         # 转换字符串为十六进制字节数据
        #         # 移除所有空格并确保字符串为偶数长度
        #         command = command.replace(" ", "")
        #         if len(command) % 2 != 0:
        #             command = "0" + command
                
        #         try:
        #             # 将字符串转换为字节数据
        #             hex_data = bytes.fromhex(command)
                    
        #             # 记录发送的数据
        #             hex_display = ' '.join([f"{byte:02X}" for byte in hex_data])
        #             formatted_data = f"[{timestamp}] Ack: {hex_display}"
        #             print(formatted_data)

        #             # self.data_received.emit(hex_data)  # Emit bytes directly
                    
        #             # 发送数据
        #             self.serial_port.write(hex_data)

                    
        #         except ValueError as e:
        #             print(f"Invalid hex string: {command}")
        #             return
                    
        #     except Exception as e:
        #         print(f"Error sending command: {e}")
        # else:
        #     print("Serial port is not open.")
        """发送命令到串口"""
        try:
            # 将命令字符串转换为字节
            if isinstance(command, str):
                # 处理十六进制字符串 (例如 "10 02 21 00...")
                cmd_bytes = bytearray.fromhex(command)
            else:
                # 处理已经是字节的情况
                cmd_bytes = command
                
            # 发送到串口
            self.serial_port.write(cmd_bytes)
            
            # 通知命令已发送（发送字节数据）- 将bytearray转换为bytes
            self.command_sent.emit(bytes(cmd_bytes))
            
            
            return True
        except Exception as e:
            print(f"发送命令失败: {str(e)}")
            return False

    def read_data(self):
        while self.running and self.serial_port and self.serial_port.is_open:
            try:
                if self.serial_port.in_waiting:
                    data = self.serial_port.read(self.serial_port.in_waiting)
                    if data:
                        self.data_received.emit(data)  # Emit bytes directly
            except Exception as e:
                print(f"Error reading from serial port: {e}")
            time.sleep(0.01)  # Changed from threading.sleep to time.sleep

    @staticmethod
    def list_ports():
        return [port.device for port in serial.tools.list_ports.comports()]