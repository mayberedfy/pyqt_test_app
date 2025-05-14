from datetime import datetime
import serial
import threading
import time
from PyQt6.QtCore import QObject, pyqtSignal


class SerialController(QObject):
    data_received = pyqtSignal(bytearray)
    command_sent = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.serial_port = None
        self.running = False
        self.data_buffer = bytearray()  # 添加数据缓冲区
        self.frame_start = 0x10  # 帧起始标记
        self.frame_end = 0x03    # 帧结束标记
        self.escape_byte = 0x10  # 转义字节

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
        """发送命令到串口"""
        try:
            
            # 将命令字符串转换为字节
            
            if isinstance(command, str):
                # 处理十六进制字符串 (例如 "10 02 21 00...")
                # cmd_bytes = bytearray.fromhex(command)
                # 清理字符串，只保留有效的十六进制字符
                clean_hex = ''.join(c for c in command if c.isalnum() or c.isspace())
                cmd_bytes = bytearray.fromhex(clean_hex)
            else:
                # 处理已经是字节的情况
                cmd_bytes = command
                
            # 发送到串口
            self.serial_port.write(cmd_bytes)
            
            # 通知命令已发送（发送字节数据）- 将bytes转换为hex字符串
            hex_str = ' '.join(f'{b:02x}' for b in cmd_bytes)
            self.command_sent.emit(hex_str)
            
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
                        self.data_received.emit(bytearray(data))  # Convert bytes to bytearray
            except Exception as e:
                print(f"Error reading from serial port: {e}")
            time.sleep(0.01)  # Changed from threading.sleep to time.sleep

    def read_serial(self):
        """读取串口数据的线程方法"""
        while self.running:
            try:
                if self.serial_port.in_waiting > 0:
                    # 读取所有可用数据
                    raw_data = self.serial_port.read(self.serial_port.in_waiting)
                    
                    # 将新数据添加到缓冲区
                    self.data_buffer.extend(raw_data)
                    
                    # 处理缓冲区中的完整帧
                    self.process_buffer()
                    
            except Exception as e:
                print(f"读取串口数据时发生错误: {str(e)}")
                break
                
            # 小暂停，避免占用过多CPU
            time.sleep(0.01)

    def process_buffer(self):
        """处理缓冲区中的数据，提取完整帧"""
        # 确保缓冲区有足够数据
        while len(self.data_buffer) >= 4:  # 最小帧长度
            # 查找帧起始
            try:
                start_idx = self.data_buffer.index(self.frame_start)
                
                # 移除起始位置之前的数据
                if start_idx > 0:
                    self.data_buffer = self.data_buffer[start_idx:]
                    
                # 如果缓冲区第二个字节不是0x02，可能不是有效帧
                if len(self.data_buffer) > 1 and self.data_buffer[1] != 0x02:
                    self.data_buffer = self.data_buffer[1:]
                    continue
                    
                # 查找帧结束
                try:
                    # 从第二个字节开始查找帧结束标记
                    end_idx = self.data_buffer.index(self.frame_end, 1)
                    
                    # 提取完整帧
                    frame = self.data_buffer[:end_idx+1]
                    
                    # 从缓冲区移除已处理的数据
                    self.data_buffer = self.data_buffer[end_idx+1:]
                    
                    # 发送完整帧
                    if len(frame) >= 4:  # 确保帧长度有效
                        self.data_received.emit(frame)
                        
                except ValueError:
                    # 未找到结束标记，等待更多数据
                    break
                    
            except ValueError:
                # 未找到起始标记，清空缓冲区
                self.data_buffer.clear()
                break

    @staticmethod
    def list_ports():
        return [port.device for port in serial.tools.list_ports.comports()]