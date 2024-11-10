from datetime import datetime
from typing import Dict, List
import requests
import os


class RequestNotionDatabase(object):
    def __init__(self):
        self.header: Dict[str, str] = self._handle_header()
        self.url: str = self._hander_url()

    def _handle_header(self) -> Dict[str, str]:
        '''
        _handle_header(self): 處理 Notion API 請求的 header
        註: Notion-Version 需要去查看 Notion API 最新文件所支援的日期格式
        https://developers.notion.com/reference/versioning
        '''
        key: str = os.getenv('NOTION_API_KEY')
        if not key:
            raise ValueError('環境變數沒有找到 NOTION_API_KEY 的值')

        return {
            'Authorization': 'Bearer ' + key,
            'Content-Type': 'application/json',
            'Notion-Version': '2022-06-28'
        }

    def _hander_url(self) -> str:
        '''
        _hander_url(self): 處理請求目標 Notion Database 的 url, 需要透過 Notion Connection 連結的資料庫
        # 可參考 Notion API 申請方式
        '''
        database_id: str = os.getenv('TARGET_DATABASE_ID')
        if not database_id:
            raise ValueError('環境變數沒有找到 TARGET_DATABASE_ID 的值')

        return f'https://api.notion.com/v1/databases/{database_id}/query'

    def get_database_json(self):
        '''
        get_database_json(self): 回傳 database JSON 的資料格式
        註: API 僅允許一次回傳 100 筆資料，若超過則使用 next_cursor 作為參數發送下一個請求，來分批接收資料
        '''
        response = requests.post(url=self.url, headers=self.header)
        return response.json()


class PageOperator(RequestNotionDatabase):
    def __init__(self, currentDate: str = None):
        super().__init__()
        # 僅 100 筆以內的資料
        self.data: List[Dict] = super().get_database_json().get('results', [])
        self.pageObject: Dict = self._analyze_pages()
        self.currentDate: str = currentDate if currentDate else str(
            datetime.today().date())

    def _analyze_pages(self) -> Dict:
        '''
        _analyze_pages(self): 分析 page 的 json 資訊(例如: id, icon, parent 等), 回傳 dict() 格式
        '''
        pages_info = dict()
        for data in self.data:
            # 使用任務日期當作 key
            task_date = data["properties"]["Date"]["date"]["start"]
            pages_info[task_date] = {
                "page_id": data["id"],
                "icon": data["icon"],
                "parent": data["parent"],  # database id
                "properties": data["properties"],
            }

        return pages_info

    def get_page_json(self):
        '''
        get_page_json(self): 回傳當前日期頁面的 json
        '''
        page_id: str = self.pageObject[self.currentDate]["page_id"]
        url: str = f'https://api.notion.com/v1/blocks/{page_id}/children'

        # 僅 100 筆以內的資料
        response = requests.get(url=url, headers=self.header)
        return response.json()

    def get_page_contents(self) -> List[Dict]:
        '''
        get_page_contents(self): 取得 page 的文字內容(如: text, to-do 等)
        '''
        data = self.get_page_json().get('results', [])
        content_list: List[Dict] = list()

        for block in data:
            content_info: Dict = {
                "parent": block["parent"], "type": block["type"], }

            notion_type: Dict = block[block["type"]]
            if block["type"] == "to_do":
                content_info["checked"] = notion_type.get("checked", False)

            if len(notion_type["rich_text"]) != 0:
                content_text = notion_type["rich_text"][0].get(
                    "plain_text", [])
                content_info["content_text"] = content_text

            content_list.append(content_info)

        return content_list


# page_obj = PageOperator()
# print(page_obj.get_page_contents())
