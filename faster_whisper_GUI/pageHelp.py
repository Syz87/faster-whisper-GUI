# coding:utf-8
"""
页面内使用说明组件（可折叠卡片，风格跟随 qfluentwidgets 主题）。

各功能页面在 __init__ 里调用 create_help_card(...) 插入即可，
说明正文统一放在 helpContent.py。
"""
from PySide6.QtCore import Qt, QSize
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTextBrowser,
    QSizePolicy,
)

from qfluentwidgets import (
    CardWidget,
    BodyLabel,
    StrongBodyLabel,
    TransparentToolButton,
    IconWidget,
    FluentIcon,
    isDarkTheme,
)

_BROWSER_QSS_LIGHT = """
QTextBrowser {
    background: transparent;
    border: none;
    color: #303030;
}
"""

_BROWSER_QSS_DARK = """
QTextBrowser {
    background: transparent;
    border: none;
    color: #E4E4E7;
}
"""


class HelpCard(CardWidget):
    """可折叠的使用说明卡片。

    收起时只占一行标题，展开后显示完整说明（内部可滚动）。
    """

    def __init__(
        self,
        html: str,
        title: str = "使用说明（点开看详细说明）",
        expanded: bool = False,
        content_height: int = 460,
        parent=None,
    ):
        super().__init__(parent)
        self.html = html
        self.content_height = content_height
        self._expanded = expanded

        self.setBorderRadius(8)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum)

        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.setContentsMargins(16, 10, 16, 10)
        self.vBoxLayout.setSpacing(6)

        # ---------- 标题行 ----------
        self.headerLayout = QHBoxLayout()
        self.headerLayout.setContentsMargins(0, 0, 0, 0)
        self.headerLayout.setSpacing(8)

        self.iconWidget = IconWidget(FluentIcon.INFO, self)
        self.iconWidget.setFixedSize(16, 16)

        self.titleLabel = StrongBodyLabel(title, self)

        self.toggleButton = TransparentToolButton(self)
        self.toggleButton.setFixedSize(28, 28)
        self.toggleButton.setIcon(
            FluentIcon.UP if expanded else FluentIcon.DOWN
        )
        self.toggleButton.setToolTip("展开 / 收起说明")
        self.toggleButton.clicked.connect(self.toggle)

        self.headerLayout.addWidget(self.iconWidget, 0, Qt.AlignmentFlag.AlignVCenter)
        self.headerLayout.addWidget(self.titleLabel, 0, Qt.AlignmentFlag.AlignVCenter)
        self.headerLayout.addStretch(1)
        self.headerLayout.addWidget(self.toggleButton, 0, Qt.AlignmentFlag.AlignVCenter)

        self.vBoxLayout.addLayout(self.headerLayout)

        # ---------- 内容区 ----------
        # 大段 HTML 延迟到第一次展开时才渲染，避免拖慢启动
        self._html_loaded = False
        self.browser = QTextBrowser(self)
        self.browser.setOpenExternalLinks(True)
        self.browser.setReadOnly(True)
        self.browser.setFrameShape(QTextBrowser.NoFrame)
        self.browser.setStyleSheet(
            _BROWSER_QSS_DARK if isDarkTheme() else _BROWSER_QSS_LIGHT
        )
        self.browser.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.browser.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.browser.document().setDocumentMargin(4)
        self.browser.setMinimumHeight(content_height)
        self.browser.setMaximumHeight(content_height)
        self.vBoxLayout.addWidget(self.browser)

        if expanded:
            self._load_html()

        # 让整张卡片可点（qfluentwidgets 的 CardWidget 在 mouseRelease 时发 clicked）
        self.setClickEnabled(True)
        self.clicked.connect(self.toggle)

        self.browser.setVisible(expanded)
        if not expanded:
            self.setMaximumHeight(58)

    def _load_html(self):
        if not self._html_loaded:
            self.browser.setHtml(self.html)
            self._html_loaded = True

    def toggle(self):
        self._expanded = not self._expanded
        if self._expanded:
            self._load_html()
        self.browser.setVisible(self._expanded)
        self.toggleButton.setIcon(
            FluentIcon.UP if self._expanded else FluentIcon.DOWN
        )
        if self._expanded:
            self.setMaximumHeight(16777215)
        else:
            self.setMaximumHeight(58)


def create_help_card(
    html: str,
    title: str = "使用说明（点开看详细说明）",
    expanded: bool = False,
    content_height: int = 460,
) -> HelpCard:
    return HelpCard(html, title=title, expanded=expanded, content_height=content_height)


# ---------- 兼容旧调用 ----------
def create_help_box(html: str, min_height: int = 96, max_height: int = 260) -> QTextBrowser:
    """保留旧接口：需要固定高度说明框时用。"""
    box = QTextBrowser()
    box.setHtml(html)
    box.setOpenExternalLinks(True)
    box.setReadOnly(True)
    box.setFrameShape(QTextBrowser.NoFrame)
    box.setStyleSheet(_BROWSER_QSS_DARK if isDarkTheme() else _BROWSER_QSS_LIGHT)
    box.setMinimumHeight(min_height)
    box.setMaximumHeight(max_height)
    box.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
    return box


def help_html(title: str, body: str) -> str:
    """统一的说明正文外壳。"""
    return (
        "<div style='font-size:10.5pt;line-height:170%;'>"
        + (f"<b>{title}</b><br>" if title else "")
        + body
        + "</div>"
    )


# 表格样式片段，供 helpContent 复用
def table(headers, rows, widths=None, highlight_rows=()):
    """生成一个跟主题合得来的表格 HTML。

    headers: 表头文字列表
    rows:    二维列表
    widths:  每列宽度百分比（可选）
    highlight_rows: 需要整行加粗的行号（0 基）
    """
    border = "rgba(255,255,255,0.14)" if isDarkTheme() else "rgba(0,0,0,0.10)"
    head_bg = "rgba(255,255,255,0.06)" if isDarkTheme() else "rgba(0,0,0,0.04)"
    out = [
        "<table width='100%' cellspacing='0' cellpadding='0' "
        "style='border-collapse:collapse;font-size:9.8pt;margin:8px 0 14px 0;'>"
    ]
    # 表头
    out.append("<tr>")
    for i, h in enumerate(headers):
        w = f" width='{widths[i]}%'" if widths else ""
        out.append(
            f"<td{w} style='background:{head_bg};border-bottom:1px solid {border};"
            f"padding:8px 10px;line-height:150%;'><b>{h}</b></td>"
        )
    out.append("</tr>")
    # 数据行
    for r_idx, row in enumerate(rows):
        bold = r_idx in highlight_rows
        out.append("<tr>")
        for c_idx, cell in enumerate(row):
            content = f"<b>{cell}</b>" if bold or c_idx == 0 else str(cell)
            w = f" width='{widths[c_idx]}%'" if widths and c_idx < len(widths) else ""
            out.append(
                f"<td{w} style='border-bottom:1px solid {border};"
                f"vertical-align:top;padding:8px 10px;line-height:155%;'>"
                f"{content}</td>"
            )
        out.append("</tr>")
    out.append("</table>")
    return "".join(out)
