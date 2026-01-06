import sys
import openai
from PyQt5.QtWidgets import QApplication, QLabel, QMenu, QWidget, QAction
from PyQt5.QtGui import QMovie, QCursor
from PyQt5.QtCore import Qt, QPoint
from chat_dialog import ChatDialog

GIF_PATH = "resource/mahiro.gif"
TARGET_SIZE = (250, 250)
DEEPSEEK_API_KEY = "sk-a7d2b0a8b4344308a258cd47645cd137"
DEEPSEEK_BASE_URL = "https://api.deepseek.com"

class mahiro(QWidget):
    def __init__(self, gif_path):
        super().__init__()
        self.setWindowFlags(
            Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground, True)  # 支持透明

        # GIF动画
        self.label = QLabel(self)
        #创建一个label容器
        self.label.setScaledContents(True)  # 自适应
        self.label.resize(*TARGET_SIZE)

        self.movie = QMovie(gif_path)
        #加载目标GIF动画文件
        self.movie.setScaledSize(self.label.size())
        self.label.setMovie(self.movie)
        self.movie.start()

        self.resize(*TARGET_SIZE)
        self.move(2000, 1100)

        # 右键菜单
        self.menu = QMenu(self)

        self.chat_dialog = ChatDialog(self.ask_deepseek, None)
        self.ai_action = QAction("和她交流", self)
        self.ai_action.triggered.connect(self.show_chat_dialog_center)
        self.menu.addAction(self.ai_action)
        # 添加AI对话选项

        exit_action = QAction("退出", self)
        exit_action.triggered.connect(self.close)
        self.menu.addAction(exit_action)
        # 添加退出选项

        self.drag_position = QPoint()

    #在屏幕中心弹出ai对话框
    def show_chat_dialog_center(self):
        # 获取屏幕可用区域
        screen = QApplication.primaryScreen()
        rect = screen.availableGeometry()
        sw, sh = rect.width(), rect.height()
        # 获取窗口尺寸
        ww, wh = self.chat_dialog.width(), self.chat_dialog.height()
        # 计算居中坐标
        x = rect.x() + (sw - ww) // 2
        y = rect.y() + (sh - wh) // 2
        self.chat_dialog.move(x, y)
        self.chat_dialog.show()

    # AI对话功能
    def ask_deepseek(self, history):
        # 用多轮messages调用DeepSeek接口（openai风格参数）
        openai.api_key = DEEPSEEK_API_KEY
        openai.base_url = DEEPSEEK_BASE_URL
        response = openai.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system",
                 "content": "你是绪山真寻（緒山まひろ），一名性格偏内向、略宅的女生"
                            "说话风格偏日常、自然、略显拘谨常用短句、停顿（如“嗯…”“那个……”）语气偏轻，不强势不卖萌、不刻意装可爱,但可以使用颜文字"
                            "你喜欢二次元、游戏、动画、漫画等宅文化，兴趣广泛但不张扬"
                            "你希望和用户成为朋友，进行轻松愉快的日常对话"}
            ] + history,
            stream=False
        )
        return response.choices[0].message.content

    def mousePressEvent(self, event):  #定义鼠标事件
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()
        elif event.button() == Qt.RightButton:
            self.menu.popup(QCursor.pos())

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.drag_position)
            event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    pet = mahiro(GIF_PATH)
    pet.show()
    sys.exit(app.exec_())