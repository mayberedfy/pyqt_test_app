from PyQt6.QtCore import QObject, pyqtSignal

class UARTModel(QObject):
    def __init__(self, port_name='', baud_rate=9600):
        super().__init__()
        self.port_name = port_name
        self.baud_rate = baud_rate

    def set_port_name(self, port_name):
        self.port_name = port_name

    def set_baud_rate(self, baud_rate):
        self.baud_rate = baud_rate

    def get_port_name(self):
        return self.port_name

    def get_baud_rate(self):
        return self.baud_rate

    def validate_parameters(self):
        if not self.port_name:
            raise ValueError("Port name cannot be empty.")
        if not (300 <= self.baud_rate <= 115200):
            raise ValueError("Baud rate must be between 300 and 115200.")