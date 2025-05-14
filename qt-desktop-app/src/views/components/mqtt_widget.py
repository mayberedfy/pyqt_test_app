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
        
        # 创建主布局 - 使用网格布局
        self.main_layout = QGridLayout(self)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(10)  # 设置网格间距
        
        # 调整行列拉伸比例 - 减小上方行的高度比例
        self.main_layout.setColumnStretch(0, 1)  # 左侧列
        self.main_layout.setColumnStretch(1, 1)  # 右侧列
        self.main_layout.setRowStretch(0, 1)    # 上方行 (从1改为1)
        self.main_layout.setRowStretch(1, 3)    # 下方行 (从2改为3，增加下方行的比例)
        
        # 创建四个区域
        self._create_connection_section()  # 左上角
        self._create_subscribe_section()   # 右上角
        self._create_publish_section()     # 左下角
        self._create_log_section()         # 右下角
        
        # 连接信号
        self.message_received.connect(self._on_message_received)
        self.connection_changed.connect(self._on_connection_changed)

    def _create_connection_section(self):
        """创建MQTT连接设置区域 - 左上方"""
        conn_frame = QFrame()
        conn_frame.setFrameStyle(QFrame.Shape.Box)
        
        conn_layout = QGridLayout(conn_frame)
        conn_layout.setColumnStretch(2, 1)  
        # 减小垂直间距
        conn_layout.setVerticalSpacing(5)
        conn_layout.setContentsMargins(8, 8, 8, 8)  # 减小内边距
        
        # 添加标题
        title = QLabel("MQTT连接设置")
        title.setFont(QFont("Arial", 11, QFont.Weight.Bold))  # 减小字体
        conn_layout.addWidget(title, 0, 0, 1, 4)
        
        # 服务器设置
        conn_layout.addWidget(QLabel("Broker:"), 1, 0)
        self.broker_input = QLineEdit("localhost")
        # 减小输入框的高度
        self.broker_input.setFixedHeight(24)
        conn_layout.addWidget(self.broker_input, 1, 1)
        
        conn_layout.addWidget(QLabel("Port:"), 1, 2)
        self.port_input = QLineEdit("1883")
        self.port_input.setFixedHeight(24)
        conn_layout.addWidget(self.port_input, 1, 3)
        
        # 用户认证
        conn_layout.addWidget(QLabel("Username:"), 2, 0)
        self.username_input = QLineEdit()
        self.username_input.setFixedHeight(24)
        conn_layout.addWidget(self.username_input, 2, 1)
        
        conn_layout.addWidget(QLabel("Password:"), 2, 2)
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setFixedHeight(24)
        conn_layout.addWidget(self.password_input, 2, 3)
        
        # 连接按钮
        self.connect_button = QPushButton("Connect")
        self.connect_button.setFixedHeight(26)  # 设置合适的按钮高度
        self.connect_button.clicked.connect(self.toggle_connection)
        conn_layout.addWidget(self.connect_button, 3, 3)
        
        # 添加到主布局 - 左上方(0,0)
        self.main_layout.addWidget(conn_frame, 0, 0)

    def _create_subscribe_section(self):
        """创建订阅主题区域 - 右上方"""
        subscribe_frame = QFrame()
        subscribe_frame.setFrameStyle(QFrame.Shape.Box)
        
        subscribe_layout = QVBoxLayout(subscribe_frame)
        # 减少内部间距
        subscribe_layout.setContentsMargins(8, 8, 8, 8)
        subscribe_layout.setSpacing(5)  # 减少垂直间距
        
        # 标题
        subscribe_title = QLabel("订阅主题")
        subscribe_title.setFont(QFont("Arial", 11, QFont.Weight.Bold))  # 减小字体
        subscribe_layout.addWidget(subscribe_title)
        
        # 主题输入
        topic_layout = QHBoxLayout()
        topic_layout.setSpacing(5)
        topic_layout.addWidget(QLabel("Topic:"))
        self.subscribe_topic = QLineEdit()
        self.subscribe_topic.setFixedHeight(24)  # 减小高度
        topic_layout.addWidget(self.subscribe_topic)
        subscribe_layout.addLayout(topic_layout)
        
        # QoS选择 - 可以使用水平布局与按钮并排
        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(5)
        
        qos_section = QHBoxLayout()
        qos_section.addWidget(QLabel("QoS:"))
        self.qos_combo = QComboBox()
        self.qos_combo.addItems(["0", "1", "2"])
        self.qos_combo.setFixedHeight(24)  # 减小高度
        qos_section.addWidget(self.qos_combo)
        qos_section.addStretch()
        
        controls_layout.addLayout(qos_section)
        
        # 将订阅和取消订阅按钮放在水平布局中
        self.subscribe_button = QPushButton("订阅")
        self.subscribe_button.setFixedHeight(26)  # 减小高度
        self.subscribe_button.clicked.connect(self._subscribe_topic)
        
        self.unsubscribe_button = QPushButton("取消订阅") 
        self.unsubscribe_button.setFixedHeight(26)  # 减小高度
        self.unsubscribe_button.clicked.connect(self._unsubscribe_topic)
        
        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(self.subscribe_button)
        buttons_layout.addWidget(self.unsubscribe_button)
        
        subscribe_layout.addLayout(controls_layout)
        subscribe_layout.addLayout(buttons_layout)
        
        # 不再需要额外的弹性空间
        # subscribe_layout.addStretch() 
        
        # 添加到主布局 - 右上方(0,1)
        self.main_layout.addWidget(subscribe_frame, 0, 1)

    def _create_publish_section(self):
        """创建发布消息区域 - 左下方"""
        publish_frame = QFrame()
        publish_frame.setFrameStyle(QFrame.Shape.Box)
        
        publish_layout = QVBoxLayout(publish_frame)
        publish_layout.setContentsMargins(8, 8, 8, 8)  # 减小内边距
        publish_layout.setSpacing(5)  # 减少垂直间距
        
        # 标题
        publish_title = QLabel("发布信息")
        publish_title.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        publish_layout.addWidget(publish_title)
        
        # 主题输入
        topic_layout = QHBoxLayout()
        topic_layout.setSpacing(5)
        topic_layout.addWidget(QLabel("Topic:"))
        self.publish_topic = QLineEdit()
        self.publish_topic.setFixedHeight(24)  # 减小高度
        topic_layout.addWidget(self.publish_topic)
        publish_layout.addLayout(topic_layout)
        
        # 消息输入
        publish_layout.addWidget(QLabel("Message:"))
        self.publish_message = QTextEdit()
        self.publish_message.setPlaceholderText("输入要发布的消息")
        publish_layout.addWidget(self.publish_message)
        
        # 发布按钮
        self.publish_button = QPushButton("发布")
        self.publish_button.setFixedHeight(26)  # 减小高度
        self.publish_button.clicked.connect(self._publish_message)
        publish_layout.addWidget(self.publish_button)
        
        # 添加到主布局 - 左下方(1,0)
        self.main_layout.addWidget(publish_frame, 1, 0)

    def _create_log_section(self):
        """创建消息日志区域 - 右下方"""
        log_frame = QFrame()
        log_frame.setFrameStyle(QFrame.Shape.Box)
        
        log_layout = QVBoxLayout(log_frame)
        log_layout.setContentsMargins(8, 8, 8, 8)  # 减小内边距
        log_layout.setSpacing(5)  # 减少垂直间距
        
        # 标题
        log_title = QLabel("信息日志")
        log_title.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        log_layout.addWidget(log_title)
        
        # 日志文本框
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        log_layout.addWidget(self.log_text)
        
        # 清除按钮
        self.clear_button = QPushButton("清除日志")
        self.clear_button.setFixedHeight(26)  # 减小高度
        self.clear_button.clicked.connect(self.log_text.clear)
        log_layout.addWidget(self.clear_button)
        
        # 添加到主布局 - 右下方(1,1)
        self.main_layout.addWidget(log_frame, 1, 1)

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