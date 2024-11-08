from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QFont
from datetime import date, datetime, timedelta
from typing import Dict
import sys
import os


class DatePicker(object):
    '''
    DatePicker(): 處理與日期相關的 class

    methods:
    format_date(): 格式化日期時間
    previous_day(): 上一天
    next_day(): 下一天
    '''

    def __init__(self, current: date = None):
        self.current: date = current if current else datetime.today()

    def format_date(self) -> str:
        '''
        format_date(self): 回傳格式化日期時間, yyyy-mm-dd
        '''
        return self.current.strftime('%Y-%m-%d')

    def previous_day(self) -> date:
        '''
        previous_day(self): 回傳昨天的日期, date
        '''
        self.current -= timedelta(days=1)
        return self.current

    def next_day(self) -> date:
        '''
        next_day(self): 回傳明天的日期, date
        '''
        self.current += timedelta(days=1)
        return self.current


class DesktopWidget(QMainWindow, DatePicker):
    """
    建立 Notion Widget 的 UI 介面
    """

    def __init__(self):
        QMainWindow.__init__(self)
        DatePicker.__init__(self)

        # UI 的相關屬性
        self.dark: bool = False  # 當前背景是 Dark 還是 Bright
        self.windows_style: Dict = {
            'bright': {
                'window-bg': '',
                'text-color': 'black',
                'btn-border': 'rgb(192, 192, 192)',
                'btn-bg-color': 'white',
                'btn-bg-hover': 'rgb(224, 224, 224)'
            },
            'dark': {
                'window-bg': 'rgb(64, 64, 64)',
                'text-color': 'white',
                'btn-border': 'rgb(192, 192, 192)',
                'btn-bg-color': '',
                'btn-bg-hover': 'rgb(104, 198, 104)'
            }
        }

        self._windows_setting()
        self.ui()

    def _windows_setting(self):
        '''
        _windows_setting(self): 視窗的基本屬性設定
        windowIcon 使用絕對路徑抓取，在 images 資料夾底下
        '''
        self.setObjectName("Notion-Widget")
        self.setWindowTitle('Notion Widget')
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)

        self.setWindowIcon(QIcon(self._handle_icon_path('task.ico')))
        self.setFixedSize(320, 240)

        styles: Dict = self.windows_style['dark'] if self.dark else self.windows_style['bright']
        self.setStyleSheet(f"""
            QMainWindow{{
                background-color: {styles['window-bg']};
            }}
            QLabel {{
                color: {styles['text-color']};
                font-family: '新細明體';
                font-size: 16px;
            }}
        """)

    def _handle_icon_path(self, filename: str) -> str:
        '''
        _handle_icon_path(self, filename: str) -> str: 處理 Icon 文件的絕對路徑
        filename: str, 圖片文件的名稱
        '''
        return os.path.join(os.path.dirname(__file__), f'../images/{filename}')

    def _switch_bg_mode(self):
        '''
        _switch_bg_mode(self): 切換背景樣式，重新渲染 UI
        '''
        self.dark = not self.dark

        self._windows_setting()
        self.ui()

    def ui(self):
        '''
        ui(self): 設定視窗的基本功能元件
        '''

        # 判斷 dark mode 狀態
        if self.dark:
            mode_icon_path: str = 'bright.ico'
            styles: Dict = self.windows_style['dark']
            btn_icon_mode: str = 'dark'

        else:
            mode_icon_path: str = 'dark.ico'
            styles: Dict = self.windows_style['bright']
            btn_icon_mode: str = 'bright'
        # End.

        # -- 布局設定 --
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout()

        # - 水平布局 1 - (日期 & 背景模式)
        h1_layout = QHBoxLayout()

        # 1. 顯示當前日期
        date_label = QLabel(self.format_date(), self)

        # 2. Dark Mode Button
        darkbtn = QPushButton()

        darkbtn.setIcon(QIcon(self._handle_icon_path(mode_icon_path)))

        darkbtn.setFixedSize(36, 36)
        darkbtn.setIconSize(darkbtn.size())
        darkbtn.setCursor(Qt.PointingHandCursor)

        darkbtn.setStyleSheet(f'''
        QPushButton {{
            border: 1px solid {styles['btn-border']};
            border-radius: 16px;
            background-color: {styles['btn-bg-color']};
        }}
        QPushButton:hover{{
            background-color: {styles['btn-bg-hover']};
        }}
        ''')
        darkbtn.clicked.connect(self._switch_bg_mode)

        h1_layout.addWidget(date_label)
        h1_layout.addWidget(darkbtn)
        # - End. -

        main_layout.addLayout(h1_layout)

        # - 垂直布局 1 - (內容區塊)
        v1_layout = QVBoxLayout()

        # 3. Notion 內容區塊
        section_label = QLabel('Content Section', self)
        v1_layout.addWidget(section_label)
        # - End. -

        main_layout.addLayout(v1_layout)

        # - 水平布局 2 - (按鈕區塊)
        # 4. Button 區塊
        h2_layout = QHBoxLayout()

        btn_icons: Dict = {
            'previous': f'previous-{btn_icon_mode}.ico',
            'create': f'create-{btn_icon_mode}.ico',
            'bullet-list': f'bullet-list-{btn_icon_mode}.ico',
            'to-do': f'to-do-{btn_icon_mode}.ico',
            'P': f'p-{btn_icon_mode}.ico',
            'next': f'next-{btn_icon_mode}.ico'
        }

        for name, path in btn_icons.items():
            button = QPushButton()
            button.setObjectName(name)
            button.setIcon(QIcon(self._handle_icon_path(path)))
            button.setFixedSize(36, 36)

            icon_size = button.size() * 0.7
            button.setIconSize(QSize(icon_size.width(), icon_size.height()))
            button.setCursor(Qt.PointingHandCursor)

            button.setStyleSheet(f"""
            QPushButton {{
                border: 1px solid {styles['btn-border']};
                border-radius: 12px;
                background-color: {styles['btn-bg-color']};
            }}
            QPushButton:hover{{
                background-color: {styles['btn-bg-hover']};
            }}
            """)

            h2_layout.addWidget(button)
            if name != 'next':
                h2_layout.addStretch()
        pass

        # - End. -
        main_layout.addLayout(h2_layout)

        central_widget.setLayout(main_layout)
        pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = DesktopWidget()
    window.show()
    sys.exit(app.exec_())
