from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QCheckBox, QLineEdit, QTextEdit
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

    def previous_day(self):
        '''
        previous_day(self): 當前天數 - 1
        '''
        self.current -= timedelta(days=1)

    def next_day(self):
        '''
        next_day(self): 當前天數 + 1
        '''
        self.current += timedelta(days=1)


class DesktopWidget(QMainWindow, DatePicker):
    """
    DesktopWidget(QMainWindow, DatePicker):
    建立 Notion Widget 的 UI 介面

    按鈕功能:
    previous: 上一天
    update:
    submit:
    bullet-list:
    to-do:
    P:
    next: 下一天
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
        self.date_label = QLabel('', self)  # 定義日期的初始狀態

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

    def _handle_btn_events(self):
        '''
        _handle_btn_events(self): 處理按鈕功能觸發時，引導相應的處理函式
        '''
        # objectName 於 ui 中的 btn_setting 的 key
        btn_object_name = self.sender().objectName()

        if btn_object_name == 'previous':
            self.previous_day()
            self.date_label.setText(self.format_date())

        if btn_object_name == 'next':
            self.next_day()
            self.date_label.setText(self.format_date())

        pass

    def _update_content_section(self):
        '''
        _update_content_section(self): 更新內容文字區塊的元件
        '''

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
        self.date_label = QLabel(self.format_date(), self)

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

        h1_layout.addWidget(self.date_label)
        h1_layout.addWidget(darkbtn)
        # - End. -

        main_layout.addLayout(h1_layout)

        # - 垂直布局 1 - (內容區塊)
        v1_layout = QVBoxLayout()

        # 3. Notion 內容區塊 (需要動態調整的)
        # UI 需要創建 QScrollArea()
        # 模擬從 API 取得資料
        list_test = [
            {'parent': {'type': 'page_id', 'page_id': '135e72f9-cc2c-807d-809b-fa06398225f4'}, 'type': 'to_do',
             'checked': False, 'content_text': '製作 Notion widget Desktop 專案'},
            {'parent': {'type': 'page_id', 'page_id': '135e72f9-cc2c-807d-809b-fa06398225f4'},
             'type': 'to_do', 'checked': True, 'content_text': '重新修正兩份履歷未來規劃的內容'},
            {'parent': {'type': 'page_id', 'page_id': '135e72f9-cc2c-807d-809b-fa06398225f4'},
                'type': 'to_do', 'checked': False, 'content_text': '投 3 ~ 5 間公司履歷'},
            {'parent': {'type': 'page_id', 'page_id': '135e72f9-cc2c-807d-809b-fa06398225f4'},
             'type': 'paragraph', 'content_text': '⇒ 下一個是理財專案'},
            {'parent': {'type': 'page_id', 'page_id': '135e72f9-cc2c-807d-809b-fa06398225f4'},
             'type': 'bulleted_list_item', 'content_text': 'AAABBB'},
            {'parent': {'type': 'page_id',
                        'page_id': '135e72f9-cc2c-807d-809b-fa06398225f4'}, 'type': 'paragraph'}
        ]
        # index 提供給 self.sender 接收具體是更改哪個元件
        for index, data in enumerate(list_test):
            if data['type'] == 'to_do':
                to_do_layout = QHBoxLayout()
                checkbox = QCheckBox()
                checkbox.setChecked(data['checked'])
                checkbox.setObjectName(f'{index}-checkbox')

                content = QTextEdit()
                content.setText(data['content_text'])
                content.setObjectName(f'{index}-to_do-content')
                content.setStyleSheet("""
                QTextEdit {
                    background-color: rgba(255, 255, 255, 0);
                    border: none;
                }
                """)

                to_do_layout.addWidget(checkbox)
                to_do_layout.addWidget(content)
                v1_layout.addLayout(to_do_layout)

            if data['type'] == 'paragraph':
                if 'content_text' in data.keys():
                    content = QTextEdit()
                    content.setText(data['content_text'])
                    content.setObjectName(f'{index}-paragraph-content')
                    content.setStyleSheet("""
                    QTextEdit {
                        background-color: rgba(255, 255, 255, 0);
                        border: none;
                    }
                    """)
                    v1_layout.addWidget(content)
                pass

            if data['type'] == 'bulleted_list_item':
                bulleted_list_layout = QHBoxLayout()
                label = QLabel('•')
                label.setObjectName(f'{index}-bulleted_list-label')

                content = QTextEdit()
                content.setText(data['content_text'])
                content.setObjectName(f'{index}-bulleted_list-content')
                content.setStyleSheet("""
                QTextEdit {
                    background-color: rgba(255, 255, 255, 0);
                    border: none;
                }
                """)

                bulleted_list_layout.addWidget(label)
                bulleted_list_layout.addWidget(content)
                v1_layout.addLayout(bulleted_list_layout)
                pass
        # - End. -

        main_layout.addLayout(v1_layout)

        # - 水平布局 2 - (按鈕區塊)
        # 4. Button 區塊
        h2_layout = QHBoxLayout()

        btn_setting: Dict = {
            'previous': {"path": f'previous-{btn_icon_mode}.ico', 'tooltip': '上一天'},
            'update': {"path": f'update-{btn_icon_mode}.ico', 'tooltip': '將 Notion 資料同步到此'},
            'submit': {"path": f'submit-{btn_icon_mode}.ico', 'tooltip': '將資料同步到 Notion'},
            'bullet-list': {"path": f'bullet-list-{btn_icon_mode}.ico', 'tooltip': '創建 Bullet-List'},
            'to-do': {"path": f'to-do-{btn_icon_mode}.ico', 'tooltip': '創建 To-do'},
            'P': {"path": f'P-{btn_icon_mode}.ico', 'tooltip': '創建 Paragraph'},
            'next': {"path": f'next-{btn_icon_mode}.ico', 'tooltip': '下一天'},
        }

        for name, obj in btn_setting.items():
            button = QPushButton()
            button.setObjectName(name)
            button.setIcon(QIcon(self._handle_icon_path(obj["path"])))
            button.setToolTip(obj["tooltip"])
            button.setFixedSize(32, 32)

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

            button.clicked.connect(self._handle_btn_events)
            h2_layout.addWidget(button)
            if name != 'next':
                h2_layout.addStretch()

            # - End. -

        main_layout.addLayout(h2_layout)
        # - End. -

        central_widget.setLayout(main_layout)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = DesktopWidget()
    window.show()
    sys.exit(app.exec_())
