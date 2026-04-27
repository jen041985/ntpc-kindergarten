import re
import time
import json
import os
from flask import Flask, jsonify, request
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from bs4 import BeautifulSoup

app = Flask(__name__, static_folder='.', static_url_path='')


# def clean_raw_text(text):
#     """🧠 恢復您之前測試成功的：正則表達式清洗大腦"""
#     data = {"type": "私立", "district": "", "name": "", "tel": "", "address": ""}
#     dist_m = re.search(r"鄉鎮：(.*?)(?:設立別|地址|$)", text)
#     type_m = re.search(r"設立別：(.*?)(?:地址|電話|$)", text)
#     addr_m = re.search(r"地址：\[?\d*\]?(.*?)(?:電話|核定人數|$)", text)
#     tel_m  = re.search(r"電話：(.*?)(?:設立許可|$)", text)
#     name_m = re.search(r"^(.*?)(?:縣市|設立別|$)", text)

#     if dist_m: data["district"] = dist_m.group(1).strip()
#     if type_m: 
#         t = type_m.group(1).strip()
#         data["type"] = "公立" if "公立" in t else ("非營利" if "非營利" in t else ("準公共" if "準公共" in t else "私立"))
#     if addr_m: data["address"] = addr_m.group(1).strip()
#     if tel_m:  data["tel"] = tel_m.group(1).strip()
#     if name_m: data["name"] = name_m.group(1).strip()
#     return data

def clean_raw_text(text):
    """🧠 強化版清洗大腦：增加準公共身分偵測"""
    data = {"type": "私立", "district": "", "name": "", "tel": "", "address": ""}
    
    # 1. 基本正則抓取
    dist_m = re.search(r"鄉鎮：(.*?)(?:設立別|地址|$)", text)
    type_m = re.search(r"設立別：(.*?)(?:地址|電話|$)", text)
    addr_m = re.search(r"地址：\[?\d*\]?(.*?)(?:電話|核定人數|$)", text)
    tel_m  = re.search(r"電話：(.*?)(?:設立許可|$)", text)
    name_m = re.search(r"^(.*?)(?:縣市|設立別|$)", text)

    # 2. 填入基本資料
    if dist_m: data["district"] = dist_m.group(1).strip()
    if addr_m: data["address"] = addr_m.group(1).strip()
    if tel_m:  data["tel"] = tel_m.group(1).strip()
    if name_m: data["name"] = name_m.group(1).strip()

    # 3. 🌟 智慧判斷「類別」
    # 優先判斷是否包含「準公共」字眼 (通常出現在園名旁或備註)
    if "準公共" in text:
        data["type"] = "準公共"
    elif type_m:
        t = type_m.group(1).strip()
        if "公立" in t: data["type"] = "公立"
        elif "非營利" in t: data["type"] = "非營利"
        else: data["type"] = "私立"
        
    return data

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/api/scrape', methods=['POST'])
def api_scrape():
    try:
        params = request.get_json() or {}
        target_district = params.get('district', '')
        target_type = params.get('type', '')
        
        print(f"\n[系統] 收到前端請求 ➔ 準備抓取區域：{target_district or '全部'}, 類別：{target_type or '全部'}")
        
        new_data = run_selenium_scraper(target_district, target_type)
        
        filename = "preschool-data.json"
        existing_data = []

        # 讀取舊資料
        if os.path.exists(filename):
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    existing_data = json.load(f)
            except Exception as e:
                print(f"[警告] 無法讀取舊資料：{e}")

        # 合併與去重
        merged_dict = {}
        for item in existing_data:
            if item.get("name"): merged_dict[item["name"]] = item
        for item in new_data:
            if item.get("name"): merged_dict[item["name"]] = item

        final_data = list(merged_dict.values())

        # 存檔
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(final_data, f, ensure_ascii=False, indent=2)
        
        print(f"[系統] 資料已成功合併！檔案目前累積共 {len(final_data)} 筆資料。")
        return jsonify(final_data)
        
    except Exception as e:
        print(f"\n[❌ 錯誤] {e}")
        return jsonify({"error": str(e)}), 500

def run_selenium_scraper(target_district, target_type):
    options = webdriver.ChromeOptions()
    # 🌟 先把 --headless 拿掉，讓您能看到瀏覽器畫面，確認沒有被卡住
    # options.add_argument('--headless') 
    driver = webdriver.Chrome(options=options)
    
    url = "https://ap.ece.moe.edu.tw/webecems/pubSearch.aspx"
    driver.get(url)
    all_data = []
    
    try:
        wait = WebDriverWait(driver, 10)
        print("[系統] 正在選擇：新北市")
        city_sel = wait.until(EC.presence_of_element_located((By.XPATH, "//select[.//option[contains(text(), '新北市')]]")))
        Select(city_sel).select_by_visible_text("新北市")
        time.sleep(1)
        
        if target_district:
            try:
                area_sel = wait.until(EC.presence_of_element_located((By.XPATH, "//select[.//option[contains(text(), '全部鄉鎮')]]")))
                Select(area_sel).select_by_visible_text(target_district)
                time.sleep(0.5)
            except: pass

        if target_type:
            categories_to_check = [target_type]
        else:
            categories_to_check = ["公立", "非營利", "準公共", "私立"]
            
        for category in ["公立", "非營利", "準公共", "私立"]:
            try:
                cb_xpath = f"//input[@type='checkbox'][following-sibling::label[contains(text(), '{category}')]] | //label[contains(text(), '{category}')]/preceding-sibling::input[@type='checkbox']"
                checkbox = driver.find_element(By.XPATH, cb_xpath)
                if (category in categories_to_check) != checkbox.is_selected(): 
                    checkbox.click()
            except: pass

        print("[系統] 點擊搜尋按鈕...")
        driver.find_element(By.XPATH, "//input[@type='submit' or @type='button'][contains(@value, '搜尋') or contains(@value, '查詢')]").click()
        
        page_num = 1
        last_page_data = []
        
        while True:
            print(f"[系統] 正在解析第 {page_num} 頁...")
            time.sleep(4) 
            
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            tables = soup.find_all('table')
            target_table = next((t for t in tables if '幼兒園' in t.text and '電話' in t.text), None)
            
            current_page_data = []
            if target_table:
                # 抓取第一層的 tr，避免抓到評鑑紀錄等隱藏子表格
                rows = target_table.find_all('tr', recursive=False)
                if not rows and target_table.find('tbody'):
                    rows = target_table.find('tbody').find_all('tr', recursive=False)
                if not rows:
                    rows = target_table.find_all('tr')
                    
                for row in rows:
                    # 🌟 關鍵修復：不數格子了，直接把整列文字合併抓出來清洗！
                    raw_text = row.get_text(" ", strip=True)
                    
                    # 過濾掉純表頭或太短的無效列
                    if "幼兒園名稱" in raw_text or len(raw_text) < 10: 
                        continue
                        
                    # 交給我們寫好的清洗大腦
                    item = clean_raw_text(raw_text)
                    
                    if item["name"]: # 只要有抓到名字，就代表這是一筆成功的資料
                        current_page_data.append(item)
            
            if current_page_data == last_page_data and len(current_page_data) > 0: 
                break 
                
            all_data.extend(current_page_data)
            last_page_data = current_page_data.copy()
            
            try:
                next_btns = driver.find_elements(By.XPATH, "//a[contains(text(), '下一頁') or contains(text(), '＞')]")
                if not next_btns or not next_btns[0].get_attribute("href"): break
                next_btns[0].click()
                page_num += 1
            except:
                break
    finally:
        driver.quit()
        print(f"[系統] 瀏覽器已關閉，共抓取 {len(all_data)} 筆資料，傳送 JSON 至前端。")
        
    return all_data

if __name__ == '__main__':
    print("="*50)
    print("🚀 伺服器啟動成功！請重新整理您的網頁。")
    print("="*50)
    app.run(debug=True, port=5000)