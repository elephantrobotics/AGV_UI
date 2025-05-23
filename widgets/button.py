import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QCheckBox
from PyQt5.QtCore import Qt, pyqtSignal
# 需配合QPropertyAnimation实现平滑过渡
from PyQt5.QtCore import QPropertyAnimation, QEasingCurve


class SwitchButton(QCheckBox):
    switched = pyqtSignal(bool)

    def __init__(self, on_color: str = "#4cd964", off_color: str = "#e9e9eb", parent=None):
        super().__init__(parent)
        self._on_color = on_color
        self._off_color = off_color
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedSize(60, 30)  # 固定尺寸确保开关大小一致

        # 初始化样式
        self._set_stylesheet(False)

        # 状态变化时更新样式
        self.stateChanged.connect(self._on_state_change)

    def switch_state(self, state: bool):
        self.setChecked(state)
        self._on_state_change(state)

    def _on_state_change(self, state):
        self._set_stylesheet(state == Qt.Checked)
        self.switched.emit(state == Qt.Checked)

    def _set_stylesheet(self, checked):
        """动态生成样式表实现平滑切换效果"""
        # thumb_color = "#ffffff"
        # thumb_color = "gray"
        thumb_color = "rgb(236, 240, 241)"
        margin = "32px" if checked else "2px"
        self.setStyleSheet(f"""
            QCheckBox {{
                background: {self._on_color if checked else self._off_color};
                border-radius: 15px;
                min-width: 60px;
                min-height: 30px;
                border: none;
            }}
            QCheckBox::indicator {{
                width: 26px;
                height: 26px;
                border-radius: 13px;
                background: {thumb_color};
                margin-left: {margin};
                margin-right: {margin};
                border: none;
            }}
            QCheckBox::indicator:hover {{
                background: #f0f0f0;
            }}

            QCheckBox::indicator:pressed {{
                background: #f0f0f0;
                border: none;
            }}
            QCheckBox:focus {{
                outline: none; 
                border: none;
            }}
        """)


class DemoWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        switch = SwitchButton()
        switch.stateChanged.connect(self.show_state)

        layout.addWidget(switch, alignment=Qt.AlignCenter)
        self.setLayout(layout)
        self.setGeometry(300, 300, 200, 100)

    def show_state(self, state):
        print("Switch状态:", "开" if state else "关")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = DemoWindow()
    window.show()
    sys.exit(app.exec_())
