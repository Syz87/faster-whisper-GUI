# coding:utf-8
"""底部任务进度条

替代原来只有转圈动画的浮动提示：显示「在做什么 + 第几个文件 + 百分比」，
跨页面常驻，任务结束自动收起。

用法：
    bar = TaskProgressBar(parent)
    bar.start("3.mp4 [1/3] 音轨分离")        # 不确定进度，显示滚动条
    bar.update_task("3.mp4 [1/3] 音轨分离", 45)  # 确定进度
    bar.finish("分离完成")                    # 收起
"""
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QLabel,
                               QStackedWidget)

from qfluentwidgets import ProgressBar, IndeterminateProgressBar, isDarkTheme, themeColor


class TaskProgressBar(QWidget):
    """底部一条：左侧任务描述，右侧百分比，下面一条进度。"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("taskProgressBar")

        self._determinate = ProgressBar()
        self._indeterminate = IndeterminateProgressBar()
        self._barStack = QStackedWidget(self)
        self._barStack.setFixedHeight(10)
        self._barStack.addWidget(self._determinate)
        self._barStack.addWidget(self._indeterminate)
        self._barStack.setCurrentWidget(self._determinate)

        # 显式上色：默认色在细条上偏淡，浅色主题下几乎看不见
        try:
            self._determinate.setCustomBarColor(themeColor(), themeColor())
        except Exception:
            pass

        self._label = QLabel("", self)
        self._label.setObjectName("taskProgressLabel")
        f = QFont()
        f.setPointSize(9)
        self._label.setFont(f)

        self._percent = QLabel("", self)
        self._percent.setObjectName("taskProgressPercent")
        self._percent.setFont(f)
        self._percent.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self._percent.setMinimumWidth(48)

        top = QHBoxLayout()
        top.setContentsMargins(0, 0, 0, 0)
        top.setSpacing(8)
        top.addWidget(self._label, 1)
        top.addWidget(self._percent, 0)

        bars = QHBoxLayout()
        bars.setContentsMargins(0, 0, 0, 0)
        bars.setSpacing(0)
        bars.addWidget(self._barStack)

        root = QVBoxLayout(self)
        root.setContentsMargins(14, 6, 14, 8)
        root.setSpacing(3)
        root.addLayout(top)
        root.addLayout(bars)

        self._apply_theme()
        self.hide()

    # ---------- 主题 ----------
    def _apply_theme(self):
        if isDarkTheme():
            color = "rgba(255,255,255,0.72)"
            tip = "rgba(255,255,255,0.45)"
            line = "rgba(255,255,255,0.10)"
        else:
            color = "rgba(0,0,0,0.72)"
            tip = "rgba(0,0,0,0.45)"
            line = "rgba(0,0,0,0.08)"
        self.setStyleSheet(
            f"#taskProgressBar {{ border-top: 1px solid {line}; }}"
            f"#taskProgressLabel {{ color: {color}; background: transparent; }}"
            f"#taskProgressPercent {{ color: {tip}; background: transparent; }}"
        )

    def set_theme_dirty(self):
        """主窗口切换主题后调用。"""
        self._apply_theme()

    # ---------- 对外接口 ----------
    def start(self, text: str, percent: int | None = None):
        """开始一个任务。percent 为 None 时显示滚动条。"""
        self._label.setText(text)
        if percent is None:
            self._barStack.setCurrentWidget(self._indeterminate)
            self._indeterminate.start()
            self._percent.setText("")
        else:
            self._indeterminate.stop()
            self._barStack.setCurrentWidget(self._determinate)
            self._determinate.setValue(max(0, min(100, int(percent))))
            self._percent.setText(f"{int(percent)}%")
        self.show()

    def update_task(self, text: str = None, percent: int = None):
        """更新文字与百分比。文字为 None 时保持原样。"""
        if text is not None:
            self._label.setText(text)
        if percent is not None:
            p = max(0, min(100, int(percent)))
            if self._barStack.currentWidget() is self._indeterminate:
                self._indeterminate.stop()
                self._barStack.setCurrentWidget(self._determinate)
            self._determinate.setValue(p)
            self._percent.setText(f"{p}%")

    def finish(self, text: str = "", delay_ms: int = 1200):
        """正常结束：显示 100% 后淡出。"""
        self._indeterminate.stop()
        self._barStack.setCurrentWidget(self._determinate)
        self._determinate.setValue(100)
        self._percent.setText("100%")
        if text:
            self._label.setText(text)
        if delay_ms <= 0:
            self.hide()
        else:
            QTimer.singleShot(delay_ms, self.hide)

    def fail(self, text: str = "已停止", delay_ms: int = 2000):
        """异常结束。"""
        self._indeterminate.stop()
        self._barStack.setCurrentWidget(self._determinate)
        if text:
            self._label.setText(text)
        self._percent.setText("")
        QTimer.singleShot(delay_ms, self.hide)
