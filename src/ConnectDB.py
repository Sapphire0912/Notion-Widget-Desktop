from typing import Dict, List
import pymongo
import os


class DBOperation(object):
    """
    DBOperation(): 處理與資料庫的 CRUD 操作

    methods:
    get_data()
    insert_data()
    update_data()
    delete_data()
    """

    def __init__(self):
        '''
        __init__(self): 連接 MongoDB 資料庫，並創建 NotionTask 資料庫與 TaskList Collection
        '''
        mongodb: str = os.getenv('LOCAL_MONGODB')
        if not mongodb:
            raise ValueError('環境變數沒有找到 LOCAL_MONGODB 的值')

        client = pymongo.MongoClient(mongodb)
        self.db = client['NotionTask']
        self.collection = self.db['TaskList']

    def find_data(self, query: Dict = {}) -> List[Dict]:
        '''
        find_data(self, query: Dict = {}): 回傳符合 query 條件的所有資料
        '''
        return list(self.collection.find(query))

    def insert_data(self, data: List[Dict]) -> List:
        '''
        insert_data(self, data: List[Dict]): 插入 Data 資料 (單筆或多筆資料皆可)，回傳 ids
        '''
        ids = self.collection.insert_many(data)
        return ids

    def update_data(self, query, new_data):
        '''
        update_data(self, query, new_data): 更新符合查詢條件的資料，並設定成 new_data 的值，回傳 update_count
        '''
        new_data = {"$set": new_data}
        update_count = self.collection.update_many(query, new_data)
        return update_count

    def delete_data(self, query):
        '''
        update_data(self, query): 刪除符合查詢條件的資料，回傳 delete_count
        '''
        delete_count = self.collection.delete_many(query)
        return delete_count


# db_test = DBOperation()
# db_test.insert_data([{'key': "value"}])
