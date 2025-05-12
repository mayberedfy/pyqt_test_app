from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QPushButton, QTextEdit, QLineEdit, QComboBox,
                           QFrame, QGridLayout)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
import paho.mqtt.client as mqtt

class MqttWidget(QWidget):
    message_received = pyqtSignal(str, str)
    connection_changed = pyqtSignal(bool)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.client = None
        self.is_connected = False
        
        # 创建主布局
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        
        # 创建连接设置区域
        self._create_connection_section()
        
        # 创建发布/订阅区域
        self._create_pubsub_section()
        
        # 创建消息日志区域
        self._create_log_section()
        
        # 连接信号
        self.message_received.connect(self._on_message_received)
        self.connection_changed.connect(self._on_connection_changed)

    def _create_connection_section(self):
        """创建MQTT连接设置区域"""
        conn_frame = QFrame()
        conn_frame.setFrameStyle(QFrame.Shape.Box)
        
        conn_layout = QGridLayout(conn_frame)
        conn_layout.setColumnStretch(2, 1)  # 第三列占据更多空间
        
        # 添加标题
        title = QLabel("MQTT连接设置")
        title.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        conn_layout.addWidget(title, 0, 0, 1, 3)
        
        # 服务器设置
        conn_layout.addWidget(QLabel("Broker:"), 1, 0)
        self.broker_input = QLineEdit("localhost")
        conn_layout.addWidget(self.broker_input, 1, 1)
        
        conn_layout.addWidget(QLabel("Port:"), 1, 2)
        self.port_input = QLineEdit("1883")
        conn_layout.addWidget(self.port_input, 1, 3)
        
        # 用户认证
        conn_layout.addWidget(QLabel("Username:"), 2, 0)
        self.username_input = QLineEdit()
        conn_layout.addWidget(self.username_input, 2, 1)
        
        conn_layout.addWidget(QLabel("Password:"), 2, 2)
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        conn_layout.addWidget(self.password_input, 2, 3)
        
        # 连接按钮
        self.connect_button = QPushButton("Connect")
        self.connect_button.clicked.connect(self.toggle_connection)
        conn_layout.addWidget(self.connect_button, 3, 3)
        
        self.main_layout.addWidget(conn_frame)

    def _create_pubsub_section(self):
        """创建发布/订阅区域"""
        pubsub_frame = QFrame()
        pubsub_frame.setFrameStyle(QFrame.Shape.Box)
        
        pubsub_layout = QHBoxLayout(pubsub_frame)
        
        # 发布区域
        publish_layout = QVBoxLayout()
        publish_title = QLabel("发布消息")
        publish_title.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        publish_layout.addWidget(publish_title)
        
        # 主题输入
        topic_layout = QHBoxLayout()
        topic_layout.addWidget(QLabel("Topic:"))
        self.publish_topic = QLineEdit()
        topic_layout.addWidget(self.publish_topic)
        publish_layout.addLayout(topic_layout)
        
        # 消息输入
        self.publish_message = QTextEdit()
        self.publish_message.setPlaceholderText("输入要发布的消息")
        self.publish_message.setMaximumHeight(100)
        publish_layout.addWidget(self.publish_message)
        
        # 发布按钮
        self.publish_button = QPushButton("发布")
        self.publish_button.clicked.connect(self._publish_message)
        publish_layout.addWidget(self.publish_button)
        
        # 订阅区域
        subscribe_layout = QVBoxLayout()
        subscribe_title = QLabel("订阅主题")
        subscribe_title.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        subscribe_layout.addWidget(subscribe_title)
        
        # 主题输入
        sub_topic_layout = QHBoxLayout()
        sub_topic_layout.addWidget(QLabel("Topic:"))
        self.subscribe_topic = QLineEdit()
        sub_topic_layout.addWidget(self.subscribe_topic)
        subscribe_layout.addWidget(self.subscribe_topic)
        
        # QoS选择
        qos_layout = QHBoxLayout()
        qos_layout.addWidget(QLabel("QoS:"))
        self.qos_combo = QComboBox()
        self.qos_combo.addItems(["0", "1", "2"])
        qos_layout.addWidget(self.qos_combo)
        qos_layout.addStretch()
        subscribe_layout.addLayout(qos_layout)
        
        # 订阅按钮
        button_layout = QHBoxLayout()
        self.subscribe_button = QPushButton("订阅")
        self.subscribe_button.clicked.connect(self._subscribe_topic)
        button_layout.addWidget(self.subscribe_button)
        
        self.unsubscribe_button = QPushButton("取消订阅")
        self.unsubscribe_button.clicked.connect(self._unsubscribe_topic)
        button_layout.addWidget(self.unsubscribe_button)
        subscribe_layout.addLayout(button_layout)
        
        # 添加到主布局
        pubsub_layout.addLayout(publish_layout)
        pubsub_layout.addLayout(subscribe_layout)
        self.main_layout.addWidget(pubsub_frame)

    def _create_log_section(self):
        """创建消息日志区域"""
        log_frame = QFrame()
        log_frame.setFrameStyle(QFrame.Shape.Box)
        
        log_layout = QVBoxLayout(log_frame)
        
        # 标题
        log_title = QLabel("消息日志")
        log_title.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        log_layout.addWidget(log_title)
        
        # 日志文本框
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMinimumHeight(200)
        log_layout.addWidget(self.log_text)
        
        # 清除按钮
        self.clear_button = QPushButton("清除日志")
        self.clear_button.clicked.connect(self.log_text.clear)
        log_layout.addWidget(self.clear_button)
        
        self.main_layout.addWidget(log_frame)

    def toggle_connection(self):
        """切换连接状态"""
        if not self.is_connected:
            self._connect_mqtt()
        else:
            self._disconnect_mqtt()

    def _connect_mqtt(self):
        """连接到MQTT Broker"""
        try:
            broker = self.broker_input.text()
            port = int(self.port_input.text())
            
            # 创建客户端
            self.client = mqtt.Client()
            
            # 设置回调
            self.client.on_connect = self._on_connect
            self.client.on_message = self._on_message
            self.client.on_disconnect = self._on_disconnect
            
            # 设置用户名密码
            username = self.username_input.text()
            password = self.password_input.text()
            if username:
                self.client.username_pw_set(username, password)
            
            # 连接
            self.client.connect(broker, port, 60)
            self.client.loop_start()
            
            self.log_message("正在连接到 MQTT Broker...")
            
        except Exception as e:
            self.log_message(f"连接错误: {str(e)}")

    def _disconnect_mqtt(self):
        """断开MQTT连接"""
        if self.client:
            self.client.loop_stop()
            self.client.disconnect()
    
    def _publish_message(self):
        """发布消息"""
        if not self.client or not self.is_connected:
            self.log_message("未连接到MQTT Broker")
            return
            
        topic = self.publish_topic.text()
        message = self.publish_message.toPlainText()
        
        if not topic:
            self.log_message("请输入发布主题")
            return
            
        try:
            result = self.client.publish(topic, message)
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                self.log_message(f"消息已发布到主题: {topic}")
                self.log_message(f"消息内容: {message}")
            else:
                self.log_message(f"发布失败，错误码: {result.rc}")
        except Exception as e:
            self.log_message(f"发布错误: {str(e)}")

    def _subscribe_topic(self):
        """订阅主题"""
        if not self.client or not self.is_connected:
            self.log_message("未连接到MQTT Broker")
            return
            
        topic = self.subscribe_topic.text()
        qos = int(self.qos_combo.currentText())
        
        if not topic:
            self.log_message("请输入订阅主题")
            return
            
        try:
            result = self.client.subscribe(topic, qos)
            if result[0] == mqtt.MQTT_ERR_SUCCESS:
                self.log_message(f"成功订阅主题: {topic} (QoS {qos})")
            else:
                self.log_message(f"订阅失败，错误码: {result[0]}")
        except Exception as e:
            self.log_message(f"订阅错误: {str(e)}")

    def _unsubscribe_topic(self):
        """取消订阅主题"""
        if not self.client or not self.is_connected:
            self.log_message("未连接到MQTT Broker")
            return
            
        topic = self.subscribe_topic.text()
        
        if not topic:
            self.log_message("请输入要取消订阅的主题")
            return
            
        try:
            result = self.client.unsubscribe(topic)
            if result[0] == mqtt.MQTT_ERR_SUCCESS:
                self.log_message(f"已取消订阅主题: {topic}")
            else:
                self.log_message(f"取消订阅失败，错误码: {result[0]}")
        except Exception as e:
            self.log_message(f"取消订阅错误: {str(e)}")

    def log_message(self, message):
        """添加消息到日志"""
        self.log_text.append(message)
        # 滚动到底部
        scrollbar = self.log_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    # MQTT回调函数
    def _on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self.is_connected = True
            self.connection_changed.emit(True)
            self.log_message("已成功连接到MQTT Broker")
        else:
            self.connection_changed.emit(False)
            self.log_message(f"连接失败，返回码: {rc}")

    def _on_disconnect(self, client, userdata, rc):
        self.is_connected = False
        self.connection_changed.emit(False)
        self.log_message("已断开连接")

    def _on_message(self, client, userdata, msg):
        try:
            payload = msg.payload.decode()
            self.message_received.emit(msg.topic, payload)
        except Exception as e:
            self.log_message(f"处理消息时出错: {str(e)}")

    def _on_message_received(self, topic, payload):
        """处理接收到的消息"""
        self.log_message(f"收到主题 '{topic}' 的消息:")
        self.log_message(f"内容: {payload}")

    def _on_connection_changed(self, connected):
        """处理连接状态变化"""
        if connected:
            self.connect_button.setText("Disconnect")
        else:
            self.connect_button.setText("Connect")
            
        # 启用/禁用相关控件
        self.broker_input.setEnabled(not connected)
        self.port_input.setEnabled(not connected)
        self.username_input.setEnabled(not connected)
        self.password_input.setEnabled(not connected)
        self.publish_button.setEnabled(connected)
        self.subscribe_button.setEnabled(connected)
        self.unsubscribe_button.setEnabled(connected)

    def cleanup(self):
        """清理资源"""
        if self.client:
            self._disconnect_mqtt()