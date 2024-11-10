from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QCheckBox, QScrollArea, QTextEdit
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon
from ApiRequest import PageOperator
from ConnectDB import DBOperation
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
        self.last_edited_time = datetime.now()

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
    update: 將 Notion 資料更新至 Widget
    submit: 將 Widget 資料傳送至 Notion
    bullet-list: 創建 bullet-list 物件
    to-do: 創建 to-do-list 物件
    P: 創建 paragraph 物件
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

        # 需要更新內容元件的變數
        self.date_label = QLabel('', self)  # 定義日期的初始狀態
        self.content_widget = QWidget()
        self.v1_layout = QVBoxLayout(self.content_widget)

        # - 創建 UI 同時需要向 db 索取資料 -
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
            QWidget {{
                background-color: {styles['window-bg']};
                color: {styles['text-color']};
                font-size: 12px;
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
        註：與 api 傳送資料的 method
        '''
        # objectName 於 ui 中的 btn_setting 的 key
        btn_object_name = self.sender().objectName()

        if btn_object_name == 'previous':
            self.previous_day()

        if btn_object_name == 'next':
            self.next_day()

        if btn_object_name == 'update':
            # 將 Notion 資料更新至 Database
            pass

        if btn_object_name == 'submit':
            # 將 Database 資料傳送至 Notion
            pass

        if btn_object_name == 'bullet-list':
            pass

        if btn_object_name == 'to-do':
            pass

        if btn_object_name == 'P':
            pass

        self.ui()  # 將整個 Widget 重新渲染一次
        pass

    def _update_content_section(self):
        '''
        _update_content_section(self): 更新內容文字區塊的元件
        註：需要清空 content_widget 元件的內容
        '''

        # - 清空布局 -
        self.content_widget = QWidget()
        self.v1_layout = QVBoxLayout(self.content_widget)
        # - End. -

        # 取得當日的 Notion 資料
        # -- 連結 MongoDB 資料庫 --
        db = DBOperation()
        datas = db.get_data({"task_date": self.format_date()})
        if len(datas) == 0:
            # 若資料不存在則呼叫 API 傳送資料，並將資料儲存至 Database 內部
            datas = PageOperator(
                currentDate=self.format_date()).get_page_contents()
            db.insert_data(data=datas)
        # -- End. --

        # index 提供給 self.sender 接收具體是更改哪個元件
        for index, data in enumerate(datas):
            if data['type'] == 'to_do':
                to_do_layout = QHBoxLayout()
                checkbox = QCheckBox()
                checkbox.setChecked(data['checked'])
                checkbox.setObjectName(f'{index}-checkbox')

                content = QTextEdit()
                content.setText(data['content_text'])
                content.setObjectName(f'{index}-to_do-content')
                content.setFixedHeight(24)
                content.setStyleSheet("""
                QTextEdit {
                    background-color: rgba(255, 255, 255, 0);
                    border: none;
                }
                """)

                to_do_layout.addWidget(checkbox)
                to_do_layout.addWidget(content)
                self.v1_layout.addLayout(to_do_layout)

            if data['type'] == 'paragraph':
                if 'content_text' in data.keys():
                    content = QTextEdit()
                    content.setText(data['content_text'])
                    content.setObjectName(f'{index}-paragraph-content')
                    content.setFixedHeight(24)
                    content.setStyleSheet("""
                    QTextEdit {
                        background-color: rgba(255, 255, 255, 0);
                        border: none;
                    }
                    """)
                    self.v1_layout.addWidget(content)
                pass

            if data['type'] == 'bulleted_list_item':
                bulleted_list_layout = QHBoxLayout()
                label = QLabel('•')
                label.setObjectName(f'{index}-bulleted_list-label')

                content = QTextEdit()
                content.setText(data['content_text'])
                content.setObjectName(f'{index}-bulleted_list-content')
                content.setFixedHeight(24)
                content.setStyleSheet("""
                QTextEdit {
                    background-color: rgba(255, 255, 255, 0);
                    border: none;
                }
                """)

                bulleted_list_layout.addWidget(label)
                bulleted_list_layout.addWidget(content)
                self.v1_layout.addLayout(bulleted_list_layout)
                pass

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

        darkbtn.setFixedSize(32, 32)

        icon_size = darkbtn.size() * 0.8
        darkbtn.setIconSize(QSize(icon_size.width(), icon_size.height()))
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
        # 3. Notion 內容區塊
        self._update_content_section()  # 需動態更新內容

        # 使用 QScrollArea() 讓每個項目可以正常顯示，超出範圍也可以滾動
        content_scroll_area = QScrollArea()
        content_scroll_area.setWidgetResizable(True)
        content_scroll_area.setWidget(self.content_widget)
        content_scroll_area.setFixedHeight(140)
        content_scroll_area.setStyleSheet(f"""
            QScrollArea {{
                border: none;
            }}
        """)
        main_layout.addWidget(content_scroll_area)
        # - End. -

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
