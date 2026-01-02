# 自主學習導航系統 (Self-Study Manager)

這是一款專為自主學習設計的全方位管理系統，整合了進度追蹤、成績分析與 **Gemini AI 錯題診斷** 技術，能根據使用者的學習弱點自動生成練習題，實現精準複習。

---

## 🌟 核心功能 (Core Features)

1. **自訂學習科目**：使用者可根據個人需求建立數學、英文、等不同學習任務。
2. **進度排程管理**：視覺化追蹤每個單元的完成進度，確保學習計畫不落後。
3. **成績管理系統**：詳實記錄每次測驗分數，並透過 ECharts 圖表呈現成績趨勢。
4. **錯題診斷複習追蹤**：
   - 記錄錯題原因與學生心得。
   - **AI 智慧診斷**：利用 Gemini AI 分析錯誤邏輯並給予解題指引。
5. **AI 根據錯題出題**：系統能針對使用者過往的錯題記錄，自動生成相似題或強化練習題，達到舉一反三的效果。

---

## 🛠️ 技術棧 (Technical Stack)

- **前端**: Vue 3.5 (Vite), Element Plus, ECharts (趨勢圖表)
- **後端**: Flask 3.1.2, SQLAlchemy (資料庫管理)
- **AI 引擎**: Google Gemini 1.5 Flash (用於診斷與自動出題)
- **資料庫**: MySQL 8.0+

---

## 🚀 快速安裝手冊

### 1. 資料庫建置
- 建立資料庫：`CREATE DATABASE selfstudy_db;`
- 執行根目錄的 `schema.sql` 以初始化資料表結構。

### 2. 後端環境 (Backend)
- 進入 `backend` 資料夾並建立虛擬環境。
- 執行 `pip install -r requirements.txt` 安裝依賴。
- 於 `.env` 設定資料庫連線資訊後，執行 `python app.py`。

### 3. 前端環境 (Frontend)
- 進入 `frontend` 資料夾。
- 執行 `npm install` 安裝套件。
- 執行 `npm run dev` 啟動系統開發介面。

---

## 📂 專案結構
- `frontend/`: Vue 3 原始碼（介面與邏輯）
- `backend/`: Flask API 與 AI 服務

- `schema.sql`: 資料庫結構定義
