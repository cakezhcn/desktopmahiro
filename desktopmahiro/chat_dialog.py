from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QListWidget, QListWidgetItem, QWidget, QLabel, QSizePolicy
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon

class ChatDialog(QDialog):
    def __init__(self, call_ai_func, parent=None):
        super().__init__(parent)
        self.setWindowTitle("和真寻对话！")
        # 使用 Qt.WindowFlags 包装位掩码，避免静态类型检查警告
        self.setWindowFlags(Qt.WindowFlags(Qt.Window | Qt.WindowMinimizeButtonHint | Qt.WindowCloseButtonHint))
        self.setWindowIcon(QIcon("resource/mahirowindowhead.jpg"))
        self.resize(1000, 700)
        self.history = []
        self.call_ai_func = call_ai_func

        self.list_widget = QListWidget(self)
        self.input_line = QLineEdit(self)
        self.input_line.setPlaceholderText("想和她说点什么呢？")
        self.send_btn = QPushButton("发送", self)
        self.send_btn.clicked.connect(self.send_message)
        self.input_line.returnPressed.connect(self.send_message)

        layout = QVBoxLayout(self)
        layout.addWidget(self.list_widget)
        input_layout = QHBoxLayout()
        input_layout.addWidget(self.input_line)
        input_layout.addWidget(self.send_btn)
        layout.addLayout(input_layout)
        self.setLayout(layout)

        # 可自定义头像图片
        self.avatar_user = "resource/user.png"      # 你自己的头像（换成你的图片路径）
        self.avatar_ai =   "resource/mahirohead.jpg" # AI人物形象头像

        # 用于在等待异步结果时保存占位项
        self._thinking_item = None

    # 发送消息给main程序处理,并显示回复
    def send_message(self):
        user_input = self.input_line.text().strip()
        if not user_input:
            return
        self.append_chat("你", user_input, avatar=self.avatar_user)
        self.history.append({"role": "user", "content": user_input})
        self.input_line.clear()
        self.send_btn.setEnabled(False)

        # 添加一个“思考中”占位，等待异步返回
        self._thinking_item = QListWidgetItem(self.list_widget)
        placeholder_widget = QWidget()
        placeholder_layout = QHBoxLayout(placeholder_widget)
        placeholder_label = QLabel("...思考中...")
        placeholder_layout.addWidget(placeholder_label)
        placeholder_layout.addStretch()
        placeholder_layout.setContentsMargins(6,6,6,6)
        placeholder_widget.setLayout(placeholder_layout)
        self._thinking_item.setSizeHint(placeholder_widget.sizeHint())
        self.list_widget.addItem(self._thinking_item)
        self.list_widget.setItemWidget(self._thinking_item, placeholder_widget)
        self.list_widget.scrollToBottom()

        # 支持两种调用方式：异步 call_ai_func(history, callback) 或 同步 call_ai_func(history)
        try:
            # 试着以异步回调的方式调用
            self.call_ai_func(self.history, self.on_ai_result)
        except TypeError:
            # 如果不能以回调方式调用，则回退到同步调用（兼容旧实现）
            try:
                ai_answer = self.call_ai_func(self.history)
                # 直接处理返回值
                self.on_ai_result(ai_answer)
            except Exception as e:
                # 替换占位并显示错误
                self._replace_thinking_with_text(f"[发生错误: {e}]")
                self.history.append({"role": "assistant", "content": f"[发生错误: {e}]"})
                self.send_btn.setEnabled(True)

    def on_ai_result(self, ai_text):
        # 回调由外部线程/函数调用，用于异步返回处理
        if ai_text is None:
            ai_text = ""
        # 移除占位并添加真实回复
        self._replace_thinking_with_text(ai_text, avatar=self.avatar_ai)
        self.history.append({"role": "assistant", "content": ai_text})
        self.send_btn.setEnabled(True)

    def _replace_thinking_with_text(self, text, avatar=None):
        # 若存在占位item，则替换为真实的消息item
        if self._thinking_item is not None:
            row = self.list_widget.row(self._thinking_item)
            self.list_widget.takeItem(row)
            self._thinking_item = None
        # 添加AI消息
        self.append_chat("AI", text, avatar=avatar or self.avatar_ai)

    # 在聊天窗口添加消息,包括头像和文本
    def append_chat(self, sender, message, avatar):
        # 创建头像标签
        avatar_label = QLabel()
        pixmap = QPixmap(avatar)
        avatar_label.setPixmap(pixmap.scaled(40,40,Qt.KeepAspectRatio, Qt.SmoothTransformation))
        avatar_label.setFixedSize(42,42)

        # 文本标签（多行自动换行）
        msg_label = QLabel(message)
        msg_label.setWordWrap(True)
        msg_label.setStyleSheet(
            "QLabel{padding:8px; border-radius:12px; background:#fffbe6; color:#444;}"
            if sender=="你" else
            "QLabel{padding:8px; border-radius:12px; background:#e6f7ff; color:#44668a;}"
        )
        msg_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        msg_label.setMaximumWidth(260)

        # 横向布局：自己左对齐，AI右对齐
        widget = QWidget()
        h_layout = QHBoxLayout(widget)
        if sender=="AI":
            h_layout.addWidget(avatar_label)
            h_layout.addWidget(msg_label)
            h_layout.addStretch()
        else:
            h_layout.addStretch()
            h_layout.addWidget(msg_label)
            h_layout.addWidget(avatar_label)
        h_layout.setContentsMargins(6,6,6,6)
        h_layout.setSpacing(8)
        widget.setLayout(h_layout)

        item = QListWidgetItem(self.list_widget)
        item.setSizeHint(widget.sizeHint())
        self.list_widget.addItem(item)
        self.list_widget.setItemWidget(item, widget)
        self.list_widget.scrollToBottom()