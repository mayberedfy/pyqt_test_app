from PyQt6.QtCore import QObject, pyqtSignal

class SerialDataController(QObject):
    # Define signals for communication
    data_received = pyqtSignal(str)
    error_occurred = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        # self.serial_port = None
        # self.running = False
        # self.read_thread = None
        # self.serial_controller = SerialController()
        # self.control_widget = ControlWidget()


