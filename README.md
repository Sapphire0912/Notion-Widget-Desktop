# 專案名稱：Notion-Widget Desktop

Notion-Widget Desktop 是一款 Notion 桌面版的小工具，專為提升生產力而設計。此工具可用於記錄每日任務和待辦事項，並提供直觀、便捷的使用者介面。小視窗會固定顯示於螢幕的最上層，方便使用者在專注於任務管理的同時，仍可無縫使用 Notion 的其他功能。該工具支持與 Notion 資料的雙向同步，確保使用者的數據在本地與 Notion 系統中保持一致。

### 使用技術

- **Python**
- **PyQt5**
- **MongoDB**
- **Notion API**
- **Postman**

### 時程

- **開發人數**：1 人
- **開始時間**：2024.11.07
- **更新時間**：2024.11.14

## 開發進度

### 11.07

- 使用 Postman 測試 Notion API
- 使用 Python 取得 API 資料

### 11.08

- 完成使用者介面基本元件 (PyQt5 + QSS)

### 11.10

- 完成 API 取得資料並更新至使用者介面
- 串接 MongoDB 暫存 Notion 與使用者資料
- 修正內容區塊的 QSS
- 完成按鈕選取日期功能

### 11.11

- 完成 MongoDB CRUD 操作
- 完成 Notion 與 MongoDB 雙向同步功能

### 11.12

- 完成創建 Notion 物件功能 (to_do, bulleted_list, paragraph)
- 修正 MongoDB 同步至 Notion 資料的問題

### 11.13

- 修正創建物件功能顯示的介面名稱問題
- 完成初版使用者介面功能
