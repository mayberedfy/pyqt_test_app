from PyQt6.QtCore import QObject, pyqtSignal
from datetime import datetime

class SerialDataController(QObject):
    # Define signals for communication
    data_received = pyqtSignal(str)
    error_occurred = pyqtSignal(str)

    def __init__(self, 
                 serial_controller=None, 
                 control_widget=None, 
                 motor_widget=None, 
                 serial_widget=None):
        super().__init__()
        self.serial_controller = serial_controller
        self.control_widget = control_widget
        self.motor_widget = motor_widget
        self.serial_widget = serial_widget

    # 控制板的串口数据处理方法
    # 控制板发送指令给电机板，此处需要解析控制板的指令并且给与应答反馈
    def control_serial_data_handle(self, data):
        try:
            
            # 记录接收到的数据
            self.record_received_data(data)

            # 转换数据为十六进制
            hex_data = ' '.join([f"{byte:02X}" for byte in data])

            # 校验接收数据是否符合预期
            # 首先校验数据长度 数据长度至少为8个字节
            data_length = len(data)
            if data_length < 8:
                print("Received data is too short:", hex_data)
                return
            
            # 校验数据头 数据头固定为0x10 0x02
            if data[0] != 0x10 or data[1] != 0x02:
                print("Received data does not start with expected header:", hex_data)
                return
            
            # 校验数据尾 数据尾固定为0x10 0x03
            if data[-2] != 0x10 or data[-1] != 0x03:
                print("Received data does not end with expected footer:", hex_data)
                return

            checksum = self.calculate_checksum(data)
            if checksum != data[-3]:
                print(f"Received data has invalid checksum: {hex_data}, expected checksum is {data[-3]}, but got {checksum}")
                return
            
            # 处理数据
            response = ""
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

                # self.control_widget.toggle_light(light_color)
                
            elif CMD == 0x20:
                # 读取软件版本：
                # 发送：CMD = 0x20  DATA0 = 0 	DATA1 = 0
                # 应答：格式同发送
                # DATA0 ~DATAn：版本信息(ASCII码)
                response = "10 02 20 56 44 32 2E 30 2E 30 BA 10 03"
                
                # self.control_widget.software_version_label.setText(software_version_str)

            # 测试控制板时，需要将应答数据发送到串口
            self.serial_controller.send_command(response) 

        except Exception as e:
            print(f"Error processing received data: {e}")
            import traceback
            traceback.print_exc()


    # 电机板的串口数据处理方法
    # 控制板主动给电机板发送指令，此处需要解析电机板的指令
    def motor_serial_data_handle(self, data):
        try:

           # 记录接收到的数据
            self.record_received_data(data)

            # 转换数据为十六进制
            hex_data = ' '.join([f"{byte:02X}" for byte in data])

            # 校验接收数据是否符合预期
            # 首先校验数据长度 数据长度至少为8个字节
            data_length = len(data)
            if data_length < 8:
                print("Received data is too short:", hex_data)
                return
            
            # 校验数据头 数据头固定为0x10 0x02
            if data[0] != 0x10 or data[1] != 0x02:
                print("Received data does not start with expected header:", hex_data)
                return
            
            # 校验数据尾 数据尾固定为0x10 0x03
            if data[-2] != 0x10 or data[-1] != 0x03:
                print("Received data does not end with expected footer:", hex_data)
                return

            checksum = self.calculate_checksum(data)
            if checksum != data[-3]:
                print(f"Received data has invalid checksum: {hex_data}, expected checksum is {data[-3]}, but got {checksum}")
                return
        

            CMD = data[2]
            if CMD == 0x83:
                # 读取档位命令：
                # 发送：CMD = 0x83  DATA0 = 速度档位信息 DATA1 = 时间档位信息
                # 读系统参数：
                # 发送：CMD = 0x83  DATA0 = 0 	DATA1 = 0
                # 应答：格式同发送 
                # 发送：CMD = 0x83  DATA0 = 速度档位信息 DATA1 = 时间档位信息;
                print("Received motor CMD 0x83")

                                
            elif CMD == 0x82:
                # 设定转速
                # 发送：CMD = 0x82  DATA0 ~DATA1：设定转速值
                # 应答：格式同发送  DATA0 = 0  DATA1 = ACK
                print("Received motor CMD 0x82")

            elif CMD == 0x81:
                # 电机运行
                # 发送：CMD = 0x81  DATA0 = 0 	DATA1 = 0
                # 应答：格式同发送  DATA0 = 0  DATA1 = ACK
                print("Received motor CMD 0x81")

            elif CMD == 0x80:
                # 电机停止
                # 发送：CMD = 0x80  DATA0 = 0 	DATA1 = 0
                # 应答：格式同发送  DATA0 = 0  DATA1 = ACK
                print("Received motor CMD 0x80")

            elif CMD == 0x21:
                # 处理命令5# 读系统参数：
                # 发送：CMD = 0x21  DATA0 = 0 	DATA1 = 0
                # 应答：格式同发送
                # DATA0：系统状态
                # DATA1~DATA2：电机转速值
                # DATA3~DATA4：电压值
                # DATA5：IPM温度值
                # DATA6~DATA7：输出功率值 
                # 此处应该解析并在界面上展示电机板的应答数据
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
                    motor_speed = (data[4] << 8) | data[5]  
                    motor_speed_actual = motor_speed / 1.0 
                    voltage_actual = voltage / 1.0  
                    temperature_actual = temperature / 1.0  
                    power_actual = power / 1.0
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
                software_version_bytes = data[3:-3]  # Excluding header, cmd, checksum and footer
                software_version_str = ''.join([chr(b) for b in software_version_bytes])
                self.motor_widget.version_label.setText(software_version_str)

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
            self.serial_widget.update_display(formatted_data)
        except Exception as e:
            print(f"Error recording received data: {e}")



    def calculate_checksum(self, data):
        """计算数据的校验和"""
        checksum = 0
        for byte in data[0:-3]:
            checksum += byte
        return checksum & 0xFF  # 取低8位
    