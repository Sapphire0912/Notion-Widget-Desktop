from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QCheckBox, QScrollArea, QTextEdit
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QFont
from ApiRequest import PageOperator
from ConnectDB import DBOperation
from datetime import date, datetime, timedelta
from typing import Dict, List
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


class HandleAPIandDB(object):
    def __init__(self):
        self.db = DBOperation()
        self.flag: bool = True  # 是否為資料庫的資料，True 為是，False 為 API 的資料
        self.data: List[Dict] = None

    def get_task_data(self, date: str) -> List[Dict]:
        '''
        get_task_data(self): 取得當日資料庫的資料，若無則向 Notion API 請求取得最新資料，回傳找到的所有資料 List[Dict]
        '''
        datas: List[Dict] = self.db.find_data({"task_date": date})
        if len(datas) == 0:
            self.flag: bool = False
            datas = PageOperator(currentDate=date).get_page_contents()
        else:
            self.flag: bool = True

        self.data = datas
        return datas

    def create_db_data(self, data: List[Dict]) -> int:
        '''
        create_db_data(self, data: List[Dict]): 若資料庫不存在資料，則需要在創建 PyQt5 元件的時候將 ObjectName 也新增至 DB 做儲存
        回傳共插入了幾筆資料至資料庫，int
        '''
        return len(self.db.insert_data(data=data).inserted_ids)

    def update_content(self, query: List[Dict], new_data):
        '''
        update_content(query, new_data): 更新資料庫的內容
        '''
        return self.db.update_data(query={"$and": query}, new_data=new_data)

    def synchronous_notion_to_db_data(self, date: str):
        '''
        synchronous_notion_to_db_data(self, date: str): 將 Notion 資料更新至 Database
        註：此處僅處理刪除 date 的 db 資料
        '''
        self.db.delete_data({"task_date": date})

    def upload_data_db_to_notion(self):
        '''
        upload_data_db_to_notion(self): 將 Database 資料更新至 Notion
        '''
        pass


class DesktopWidget(QMainWindow, DatePicker, HandleAPIandDB):
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
        HandleAPIandDB.__init__(self)

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
        self.last_edited_time_label = QLabel('', self)  # 定義最後 Notion 更新時間

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
        self.setFixedSize(360, 280)

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

    def _show_message_box(self, name: str):
        '''
        _show_message_box(self, name: str): 當使用者點選"更新"或"上傳"按鈕時的確認視窗
        '''
        message_box = QMessageBox()
        message_box.setWindowTitle('提醒訊息')
        message_box.setWindowFlags(
            message_box.windowFlags() | Qt.WindowStaysOnTopHint)
        message_box.setWindowIcon(QIcon(self._handle_icon_path('task.ico')))

        if name == 'update':
            message_box.setText('是否確定將 Notion 資料同步至本機資料庫')

        elif name == 'submit':
            message_box.setText('是否確定將本機資料庫的資料上傳至 Notion 並同步')

        message_box.setIcon(QMessageBox.Information)
        btn_ok = message_box.addButton('確認', QMessageBox.AcceptRole)
        btn_cancel = message_box.addButton('取消', QMessageBox.RejectRole)

        message_box.exec_()

        if message_box.clickedButton() == btn_ok:
            if name == "update":
                self.synchronous_notion_to_db_data(self.format_date())
                # 重新渲染 UI
                self._update_content_section()

            elif name == "submit":
                self.upload_data_db_to_notion(self.format_date())

        elif message_box.clickedButton() == btn_cancel:
            pass

    def _handle_btn_events(self):
        '''
        _handle_btn_events(self): 處理按鈕功能觸發時，引導相應的處理函式
        註：與 api 傳送資料的 method
        '''
        # objectName 於 ui 中的 btn_setting 的 key
        btn_object_name = self.sender().objectName()

        key_functions: Dict[str, function] = {
            'previous': self.previous_day,
            'next': self.next_day,
            'update': lambda: self._show_message_box(name='update'),
            'submit': lambda: self._show_message_box(name='submit'),
            'bullet-list': None,
            'to-do': None,
            'P': None
        }

        if btn_object_name in key_functions:
            key_functions[btn_object_name]()

        self.ui()  # 將整個 Widget 重新渲染一次

    def _handle_content_events(self):
        '''
        _handle_content_events(self): 處理 content 區塊中的事件。例如：更新 TextEdit 內容、CheckBox 狀態等
        註：一旦內容變動即時與 db 做更新資訊的操作
        '''
        event_object_name = self.sender().objectName()
        object_info = event_object_name.split('-')
        _, object_type, object_element = object_info[0], object_info[1], object_info[2]

        # - 更新資料庫內容 -
        query: List[Dict] = [
            {"task_date": self.format_date(), "type": object_type}
        ]
        last_edited_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        if object_element == 'checkbox':
            query.append(
                {"checkbox_ObjectName": event_object_name})

            # 取得觸發事件元件的狀態
            checkbox = self.findChild(QCheckBox, event_object_name)
            self.update_content(query=query, new_data={
                                "checked": checkbox.isChecked(),
                                "last_edited_time": last_edited_time
                                })

        elif object_element == 'content':
            query.append({"content_ObjectName": event_object_name})

            # 取得觸發事件元件的狀態
            text_edit = self.findChild(QTextEdit, event_object_name)
            self.update_content(query=query, new_data={
                                "content_text": text_edit.toPlainText(),
                                "last_edited_time": last_edited_time
                                })

        else:
            raise ValueError('Object 類型不正確')
        # - End. -

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
        datas, flag = self.get_task_data(self.format_date()), self.flag
        self.last_edited_time_label.setText(
            f"Notion 最後更新:\n{datas[0]["last_edited_time"]}")  # 顯示最後更新時間

        # index 提供給 self.sender 接收具體是更改哪個元件
        for index, data in enumerate(datas):
            if data['type'] == 'to_do':
                if not flag:
                    # - 提供資料庫資訊，用於 CRUD -
                    data["checkbox_ObjectName"] = f'{index}-to_do-checkbox'
                    data["content_ObjectName"] = f'{index}-to_do-content'
                    # - End. -

                to_do_layout = QHBoxLayout()
                checkbox = QCheckBox()
                checkbox.setChecked(data['checked'])
                checkbox.setObjectName(f'{index}-to_do-checkbox')

                content = QTextEdit()
                content.setText(data['content_text'])
                content.setObjectName(f'{index}-to_do-content')
                content.setFixedHeight(30)
                content.setStyleSheet("""
                QTextEdit {
                    background-color: rgba(255, 255, 255, 0);
                    border: none;
                }
                """)

                # - 加入事件處理 -
                checkbox.stateChanged.connect(self._handle_content_events)
                content.textChanged.connect(self._handle_content_events)
                # - End. -

                to_do_layout.addWidget(checkbox)
                to_do_layout.addWidget(content)
                self.v1_layout.addLayout(to_do_layout)

            if data['type'] == 'paragraph' and 'content_text' in data.keys():
                if not flag:
                    # - 提供資料庫資訊，用於 CRUD -
                    data["content_ObjectName"] = f'{
                        index}-paragraph-content'
                    # - End. -

                content = QTextEdit()
                content.setText(data['content_text'])
                content.setObjectName(f'{index}-paragraph-content')
                content.setFixedHeight(30)
                content.setStyleSheet("""
                QTextEdit {
                    background-color: rgba(255, 255, 255, 0);
                    border: none;
                }
                """)

                # - 加入事件處理 -
                content.textChanged.connect(self._handle_content_events)
                # - End. -

                self.v1_layout.addWidget(content)

            if data['type'] == 'bulleted_list_item':
                if not flag:
                    # - 提供資料庫資訊，用於 CRUD -
                    data["label_ObjectName"] = f'{index}-bulleted_list-label'
                    data["content_ObjectName"] = f'{
                        index}-bulleted_list-content'
                    # - End. -

                bulleted_list_layout = QHBoxLayout()
                label = QLabel('•')
                label.setObjectName(f'{index}-bulleted_list-label')

                content = QTextEdit()
                content.setText(data['content_text'])
                content.setObjectName(f'{index}-bulleted_list-content')
                content.setFixedHeight(30)
                content.setStyleSheet("""
                QTextEdit {
                    background-color: rgba(255, 255, 255, 0);
                    border: none;
                }
                """)

                # - 加入事件處理 -
                content.textChanged.connect(self._handle_content_events)
                # - End. -
                bulleted_list_layout.addWidget(label)
                bulleted_list_layout.addWidget(content)
                self.v1_layout.addLayout(bulleted_list_layout)

        if not flag:
            self.create_db_data(data=datas)

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

        # 2. 顯示 Notion 最後更新日期
        self.last_edited_time_label = QLabel("最後更新時間:\n", self)

        # 3. Dark Mode Button
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
        h1_layout.addWidget(self.last_edited_time_label)
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
