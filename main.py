from base64 import b64decode
from random import randint
from sys import exit
from time import sleep, time

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QApplication, QCheckBox, QFormLayout, QHBoxLayout, QInputDialog, QLabel
from PySide6.QtWidgets import QFrame, QLineEdit, QMainWindow, QMenu, QMessageBox, QPushButton
from PySide6.QtWidgets import QSpacerItem, QSpinBox, QSizePolicy, QSystemTrayIcon, QVBoxLayout, QWidget
from PySide6.QtWidgets import QLCDNumber
from win32api import GetSystemMetrics
from win32con import SM_CXSCREEN, SM_CYSCREEN
from win32gui import GetForegroundWindow, GetWindowRect

from img import *

class MainWindow(QMainWindow):
    """
    TODO(): 1. 托盘加鼠标悬浮显示倒计时
    """
    def __init__(self):
        super().__init__()
        # 状态量定义 #
        self.is_counting = False  # 是否正在倒计时
        self.pause = False  # 倒计时是否暂停
        ## 状态量定义 ##
        self._init_img()
        self._init_main_window()
        self._init_main_layout()
        self._init_spacer()
        self._init_LCD()
        self._init_time_setting()
        self._init_bottom_layout()
        self._init_system_tray_icon()
        self._init_gui()
        self._init_connect()

    def _init_img(self):
        """图片定义"""
        self.pic_window = QPixmap()
        self.pic_window.loadFromData(b64decode(UNKNOWN_ICON_Black_png))
        self.pic_tray = QPixmap()
        self.pic_tray.loadFromData(b64decode(UNKNOWN_ICON_White_png))

    def _init_main_window(self):
        """主窗口定义"""
        self.setWindowIcon(self.pic_window)
        self.setWindowTitle("Drink More Water")
        self.setFixedSize(320, 180)
        self.setWindowFlags(Qt.WindowStaysOnTopHint)  # 设置窗口置顶

    def _init_main_layout(self):
        """总布局定义"""
        self.widget = QWidget()
        self.layout = QVBoxLayout()
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)

    def _init_spacer(self):
        """空白定义"""
        self.top_horizontal_spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.bottom_horizontal_spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

    def _init_LCD(self):
        """LCD 表盘定义"""
        self.time_display = QLCDNumber()
        self.time_display.setFrameStyle(QFrame.NoFrame)
        self.time_display.setSegmentStyle(QLCDNumber.Filled)
        self.time_display.display("00:00")

    def _init_time_setting(self):
        """时间设置定义"""
        self.time_setting_layout = QFormLayout()
        self.time_setting_layout.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
        self.time_setting_layout.setRowWrapPolicy(QFormLayout.DontWrapRows)
        self.time_setting_layout.setLabelAlignment(Qt.AlignCenter)
        self.time_setting_layout.setFormAlignment(Qt.AlignCenter)
        self.time_setting_layout.setHorizontalSpacing(10)
        self.time_setting_layout.setVerticalSpacing(10)
        # 创建标签 #
        self.label = QLabel("间隔时间：")
        self.time_setting_layout.setWidget(0, QFormLayout.LabelRole, self.label)
        # 创建时间输入框 #
        self.spin_box = QSpinBox()
        self.spin_box.setSuffix("分钟")
        self.spin_box.setMaximum(1440)
        self.spin_box.setValue(30)
        self.time_setting_layout.setWidget(0, QFormLayout.FieldRole, self.spin_box)

    def _init_bottom_layout(self):
        """底部布局定义"""
        self.bottom_layout = QHBoxLayout()
        # 创建选择框 #
        self.check_box_layout = QVBoxLayout()
        self.check_box_layout.setSpacing(10)
        self.check_box_fullscreen = QCheckBox()
        self.check_box_fullscreen.setText("全屏下依旧提醒");
        self.check_box_layout.addWidget(self.check_box_fullscreen, 0, Qt.AlignHCenter)
        self.check_box_minimize = QCheckBox()
        self.check_box_minimize.setText("开始后自动最小化")
        self.check_box_minimize.setChecked(True)
        self.check_box_layout.addWidget(self.check_box_minimize, 0, Qt.AlignHCenter)
        self.check_box_layout.setStretch(0, 1)
        self.check_box_layout.setStretch(1, 1)
        self.bottom_layout.addLayout(self.check_box_layout)
        # 创建按钮区布局 #
        self.button_layout = QVBoxLayout()
        self.button_layout.setSpacing(10)
        self.push_button_start = QPushButton("开始自律喝水")
        self.button_layout.addWidget(self.push_button_start, 0, Qt.AlignHCenter)
        self.push_button_pause = QPushButton("暂停")
        self.button_layout.addWidget(self.push_button_pause, 0, Qt.AlignHCenter)
        self.button_layout.setStretch(0, 1)
        self.button_layout.setStretch(1, 1)
        self.bottom_layout.addLayout(self.button_layout)

    def _init_system_tray_icon(self):
        """托盘图标定义"""
        self.system_tray_icon = QSystemTrayIcon(self.pic_tray)
        self.system_tray_icon.setToolTip("Drink More Water")
        # 创建托盘菜单 #
        self.tray_menu = QMenu()
        self.action_show = self.tray_menu.addAction("显示主界面")
        self.tray_menu.addSeparator()
        self.action_exit = self.tray_menu.addAction("退出")
        self.system_tray_icon.setContextMenu(self.tray_menu)

    def _init_gui(self):
        """添加组件到主界面"""
        self.layout.addItem(self.top_horizontal_spacer)  # 顶部空白
        self.layout.addWidget(self.time_display)  # 时间显示
        self.layout.addLayout(self.time_setting_layout)  # 时间设置
        self.layout.addLayout(self.bottom_layout)  # 底部布局
        self.layout.addItem(self.bottom_horizontal_spacer)  # 底部空白
        self.widget.setLayout(self.layout)  # 总布局
        self.setCentralWidget(self.widget)

    def _init_connect(self):
        """信号与槽连接
        Notes:
            object.Signal.connect(Slot: 函数名)
        """
        self.push_button_start.clicked.connect(self._change_butt_state)  # 主界面 开始
        self.push_button_pause.clicked.connect(self._stop_timer)  # 主界面 暂停
        self.action_show.triggered.connect(self.show)  # 托盘菜单 显示主界面
        self.action_exit.triggered.connect(exit)  # 托盘菜单 退出
        self.system_tray_icon.activated.connect(self._tray_icon_proc)  # 托盘图标 鼠标事件

    @staticmethod
    def _generate_captcha() -> str:
        """随机生成验证码"""
        captcha = ""
        for i in range(4):
            flag = randint(0, 2)  # 先随机每个位置上的字符种类，数字，小写或大写
            if flag == 0:  # 再随机具体的字符
                captcha += chr(ord('0') + randint(0, 9))  # 随机增量
            elif flag == 1:
                captcha += chr(ord('A') + randint(0, 25))
            elif flag == 2:
                captcha += chr(ord('a') + randint(0, 25))
        return captcha

    @staticmethod
    def _is_fullscreen() -> bool:
        """全屏检测"""
        active_window = GetForegroundWindow()  # 获取活跃即当前窗口句柄
        _, _, w_width, w_height = GetWindowRect(active_window)  # 获取窗口大小
        width = GetSystemMetrics(SM_CXSCREEN)  # 获取实际分辨率，即缩放后分辨率
        height = GetSystemMetrics(SM_CYSCREEN)
        return w_width == width and w_height == height

    def _get_input_text(self, text: str) -> str:
        """输入框窗口
        Args:
            text: msg，信息内容
        Returns:
            输入的内容
        Notes:
            QInputDialog.getText() 返回的是 (text, state)，text 是输入的内容，state 是点击的是确认或取消，与官方 docs 描述不同
        """
        return QInputDialog.getText(self, "Drink More Water", text, QLineEdit.Normal, "", Qt.WindowStaysOnTopHint)[0]

    def _reminder(self):
        """提醒窗口"""
        if not self.check_box.isChecked():  # 先确定是否勾选全屏提醒
            while True:
                try:
                    if self._is_fullscreen():  # 每秒检查全屏状态 60 次
                        sleep(1/60)
                        QApplication.processEvents()
                    else:
                        break
                except:
                    pass
        self.show()
        def is_exit(self: MainWindow):
            msg_box = QMessageBox(
                QMessageBox.Icon.Question,
                "Drink More Water",
                "确定要退出吗？",
                flags=Qt.WindowStaysOnTopHint
            )  # 创建退出密钥确认窗口
            msg_box.setWindowIcon(self.pic_window)
            button_yes = msg_box.addButton("确定", QMessageBox.YesRole)
            button_return = msg_box.addButton("返回主界面", QMessageBox.ActionRole)
            msg_box.addButton("取消", QMessageBox.RejectRole)
            msg_box.exec()
            if msg_box.clickedButton() == button_yes:
                exit()
                return True
            elif msg_box.clickedButton() == button_return:
                return True
            else:
                return False
        EXIT_CODE = "00000"  # 退出密钥
        captcha = self._generate_captcha()  # 生成验证码
        input_text = self._get_input_text("请输入 " + captcha + " ：")  # 创建验证码输入框
        if input_text == EXIT_CODE:  # 验证码正确
            if is_exit(self):
                return
        while input_text != captcha:  # 验证码错误
            captcha = self._generate_captcha()
            input_text = self._get_input_text("输入错误！请输入 " + captcha + " ：")
            if input_text == EXIT_CODE:
                if is_exit(self):
                    return
        self._timer();

    def _reset(self):
        """重置程序"""
        self.time_display.display("00:00")

    def _change_butt_state(self):
        """开始计时后改变按钮状态"""
        if not self.is_counting:
            self.is_counting = True
            self.push_button_start.setText("停止")
            self._timer()
        else:
            self.is_counting = False
            self.push_button_start.setText("开始自律喝水")

    def _timer(self):
        """计时器"""
        if self.check_box_minimize.isChecked():
            self.hide()
        target = self.spin_box.value() * 60  # 从 spin_box 获取到的是分钟，后面需要显示秒数，所以直接转换
        diff_stop = 0  # 记录暂停时间
        start = time()
        while True:
            if self.is_counting:
                sleep(1/60)  # 每秒执行 60 次
                diff = int(time() - diff_stop - start)
                min = (target - diff) // 60
                sec = (target - diff) % 60
                int2str = lambda n : '0' + str(n) if n < 10 else str(n)  # 通过 lambda 给分钟和秒数添前导 0
                self.time_display.display(f"{int2str(min)}:{int2str(sec)}")  # 展示
                if diff >= target:
                    self.is_counting = False  # 取消倒计时状态
                    self.time_display.display("00:00")  # 重置显示
                    self._reminder()
                    return
                start_stop = time()  # 处理暂停
                while self.pause:
                    QApplication.processEvents()  # 响应事件
                diff_stop += time() - start_stop
                QApplication.processEvents()
            else:
                self._reset()
                break

    def _stop_timer(self):
        """暂停计时"""
        if self.is_counting:  # 正在倒计时暂停按钮才有用
            if not self.pause and self.push_button_pause.text() == "暂停":
                self.push_button_pause.setText("继续")
            else:
                self.push_button_pause.setText("暂停")
            self.pause = not self.pause
        else:
            return

    def _tray_icon_proc(self, reason):
        """托盘鼠标事件"""
        if reason == QSystemTrayIcon.DoubleClick:  # 双击托盘图标
            self.show()
        elif reason == QSystemTrayIcon.Context:  # 右键？
            self.system_tray_icon.contextMenu().show()

    def show(self):
        """重写 show()"""
        super().show()
        self.system_tray_icon.show()

    def closeEvent(self, event):
        """重写 closeEvent()"""
        msg_box = QMessageBox(
            QMessageBox.Icon.Question,
            "Drink More Water",
            "确定要退出吗？",
            flags=Qt.WindowStaysOnTopHint
        )  # 退出确认框
        msg_box.setWindowIcon(self.pic_window)
        button_yes = msg_box.addButton("确定", QMessageBox.YesRole)
        button_minimize = msg_box.addButton("最小化到托盘", QMessageBox.DestructiveRole)
        msg_box.addButton("取消", QMessageBox.RejectRole)
        msg_box.exec()
        if msg_box.clickedButton() == button_yes:
            event.accept()
            exit()
        elif msg_box.clickedButton() == button_minimize:
            event.ignore()
            self.hide()
        else:  # 点击窗口右上角关闭和取消为同一效果
            event.ignore()

if __name__ == '__main__':
    app = QApplication([])
    main_window = MainWindow()
    main_window.show()
    exit(app.exec())