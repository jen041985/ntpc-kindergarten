# 🏫 新北市幼兒園資料採集與查詢系統

這是一個結合 Python 爬蟲與 Web 介面的自動化工具，旨在協助特定使用者快速同步與搜尋新北市各區幼兒園的最新資訊。

## 🌟 系統特色
- **自動化採集**：使用 Selenium 模擬瀏覽器操作，精準抓取全國教保資訊網資料。
- **資料去重合併**：Python 後端具備智慧合併功能，多次抓取不同區域後會自動累加資料。
- **準公共偵測**：自動偵測「準公共」身分，提供比原始設立別更精準的分類。
- **靜態網頁查詢**：採用「方案 B」架構，資料以 JSON 格式儲存，網頁端查詢極速且不耗伺服器資源。
- **匯出功能**：支持一鍵下載整理好的 CSV 檔案（格式已優化，Excel 開啟不亂碼）。

## 🛠️ 技術棧
- **後端 (Scraper)**: Python 3, Selenium, BeautifulSoup4, Flask
- **前端 (UI)**: HTML5, CSS3 (Noto Sans TC), JavaScript (Vanilla JS)
- **資料格式**: JSON, CSV

## 🚀 使用說明

### 1. 本地資料同步 (由管理員操作)
1. 安裝必要套件：
   ```bash
   pip install flask selenium beautifulsoup4
   
2. 執行爬蟲伺服器：
   ```bash
   python app.py
   
3. 在瀏覽器打開 http://127.0.0.1:5000，選擇行政區後點擊「開始自動抓取」。

4. 抓取完成後，系統會自動生成或更新 preschool-data.json。

### 2. 線上更新 (部署至 GitHub Pages)
將更新後的 preschool-data.json 上傳至 GitHub 儲存庫。
GitHub Pages 會在 1-2 分鐘內自動更新線上網頁內容。

### 3. 線上查詢 (供特定對象使用)
直接存取 GitHub Pages 提供之網址。
輸入預設之存取密碼即可開始查詢與下載。

## 📂 檔案結構
- **app.py: Python 後端爬蟲與 Flask 伺服器邏輯。
- **index.html: 前端查詢介面與 CSV 轉換工具。
- **preschool-data.json: 系統資料庫檔案（由爬蟲產出）。
- **README.md: 專案說明文件。

## ⚠️ 免責聲明
本工具僅供學術研究與個人用途使用，資料來源為「全國教保資訊網」。請遵守相關網站之爬蟲守則，勿進行高頻率惡意抓取
