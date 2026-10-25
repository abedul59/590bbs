import json
import requests
import os
import sys
import time
import random
import re
import traceback
import webbrowser
from datetime import datetime
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

DASHBOARD_URL = "https://590bbs.vercel.app/macrowave?view=bengo"
UPLOAD_API_URL = "https://590bbs.vercel.app/api/bengo/upload"
REQUEST_TIMEOUT = (10, 60)
DEFAULT_SETTINGS = {
    "headless": True,
    "minimum_wait_seconds": 40,
    "maximum_wait_seconds": 120,
    "open_dashboard_when_finished": False,
}


def configure_working_directory():
    """讓 Python、雙擊 EXE 與排程器都從程式所在資料夾讀寫。"""
    program_path = sys.executable if getattr(sys, "frozen", False) else __file__
    os.chdir(os.path.dirname(os.path.abspath(program_path)))


def load_settings(filename="bengo_settings.json"):
    settings = dict(DEFAULT_SETTINGS)
    if not os.path.exists(filename):
        return settings
    try:
        with open(filename, "r", encoding="utf-8-sig") as handle:
            saved = json.load(handle)
        if isinstance(saved, dict):
            settings.update({key: saved[key] for key in settings if key in saved})
    except (OSError, json.JSONDecodeError) as exc:
        print(f"⚠️ 設定檔讀取失敗，改用預設值：{exc}")
    settings["minimum_wait_seconds"] = max(0, int(settings["minimum_wait_seconds"]))
    settings["maximum_wait_seconds"] = max(settings["minimum_wait_seconds"], int(settings["maximum_wait_seconds"]))
    return settings


def create_http_session():
    retry = Retry(
        total=3,
        connect=3,
        read=3,
        backoff_factor=2,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=frozenset(("GET", "POST")),
    )
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/122 Safari/537.36"
    })
    session.mount("https://", HTTPAdapter(max_retries=retry))
    return session


def validate_stock_id(value):
    stock_id = str(value).strip().upper()
    if not re.fullmatch(r"[A-Z0-9]{2,12}", stock_id):
        raise ValueError(f"股票代號格式不正確：{value!r}")
    return stock_id

# ==========================================
# 1. 讀取 CSV 設定檔 (股票清單)
# ==========================================
def read_stock_ids(filename="stock_id_settings.csv"):
    stock_ids = []
    if not os.path.exists(filename):
        print(f"❌ 錯誤：找不到設定檔 '{filename}'，請確認檔案在同目錄下。")
        with open(filename, 'w', encoding='utf-8', newline='') as f:
            f.write("2330\n2317\n2603\n")
        print(f"👉 已自動為您建立範例 '{filename}'，請填入股票代號後重新執行。")
        return []
        
    with open(filename, 'r', encoding='utf-8-sig') as f:
        for line in f:
            sid = line.strip().split(',')[0].strip()
            if not sid or sid.lower() in ("stock_id", "股票代號"):
                continue
            try:
                stock_ids.append(validate_stock_id(sid))
            except ValueError as exc:
                print(f"⚠️ 略過設定檔中的無效項目：{exc}")
    return list(dict.fromkeys(stock_ids))

# ==========================================
# 2. 核心爬蟲與計算邏輯
# ==========================================
class BengoScraper:
    def __init__(self, settings=None, session=None):
        self.settings = settings or dict(DEFAULT_SETTINGS)
        self.session = session or create_http_session()

    def clean_num(self, x):
        try:
            return float(str(x).replace(',', '').replace('%', '').strip())
        except (TypeError, ValueError):
            return 0.0

    def calculate_bengo_threshold(self, price):
        if price >= 1000: return 50
        elif 500 <= price < 1000: return 100
        elif 250 <= price < 500: return 200
        elif 125 <= price < 250: return 400
        elif 62.5 <= price < 125: return 800
        else: return 1000

    def get_stock_name_moneydj(self, stock_id):
        try:
            my_Referer = 'https://djinfo.cathaysec.com.tw/'
            headers = {'Referer': my_Referer}

            bank_url = 'https://djinfo.cathaysec.com.tw/' 
            sheet_type = 'z/zc/zca/zca_' 
            url = bank_url + sheet_type + stock_id + '.djhtm'
            
            response = self.session.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            page_text = ' '.join(soup.stripped_strings)
            match = re.search(rf'([^\s()｜|]{{1,24}})\s*\(\s*{re.escape(stock_id)}\s*\)', page_text)
            if match:
                return re.sub(r'\d+', '', match.group(1)).strip()
            title = soup.find('title')
            if title:
                candidate = title.get_text(' ', strip=True).split('(')[0].strip()
                candidate = re.sub(r'\d+', '', candidate).strip(' -|｜')
                if candidate:
                    return candidate
            return ""
        except Exception as e:
            print(f"  -> ⚠️ MoneyDJ 抓取名稱失敗: {e}")
            return ""

    def parse_main_history(self, element):
        rows = element.find_elements(By.TAG_NAME, "tr")
        data = []
        for row in rows:
            cols = row.find_elements(By.TAG_NAME, "td")
            if len(cols) < 5: continue
            
            date_idx = -1
            date_str = ""
            for i in range(min(5, len(cols))):
                txt = cols[i].text.strip()
                match = re.search(r'(\d{8})', txt)
                if match: date_idx = i; date_str = match.group(1); break
            
            if date_idx == -1: continue
            def get_val(offset): return cols[date_idx + offset].text.strip() if (date_idx + offset) < len(cols) else "0"
            try:
                price = self.clean_num(get_val(12))
                if price == 0: continue
                data.append({
                    'date': date_str,
                    'price': price,
                    'total_shares': self.clean_num(get_val(1)),
                    'total_people': int(self.clean_num(get_val(2))), 
                    'raw_400_ppl': int(self.clean_num(get_val(6))),
                    'raw_400_pct': self.clean_num(get_val(5))
                })
            except (AttributeError, IndexError, TypeError, ValueError):
                continue
        return data

    def parse_prior_table_fixed(self, soup_table):
        try:
            rows = soup_table.find_all('tr')
            if not rows: return {}

            date_list = []
            for r in range(min(5, len(rows))):
                cells = rows[r].find_all(['th', 'td'])
                for cell in cells:
                    txt = cell.get_text(strip=True)
                    match = re.search(r'(\d{8})', txt)
                    if match: date_list.append(match.group(1))
                if date_list: break
            
            if not date_list: return {}
            
            temp_data = {d: [] for d in date_list}
            for row in rows:
                cells = row.find_all(['td', 'th'])
                if not cells: continue
                name = cells[0].get_text(strip=True)
                if not any(c.isdigit() for c in name) or "合計" in name: continue
                if "*" in name: continue 

                data_cells = cells[1:]
                for i, date_str in enumerate(date_list):
                    base_idx = i * 3
                    if base_idx + 1 < len(data_cells):
                        ppl = self.clean_num(data_cells[base_idx].get_text())
                        shares = self.clean_num(data_cells[base_idx+1].get_text())
                        temp_data[date_str].append({'range': name, 'ppl': ppl, 'shares': shares})
            return temp_data
        except (AttributeError, IndexError, TypeError, ValueError):
            return {}

    def parse_graded_table_fixed(self, soup_table):
        try:
            rows = soup_table.find_all('tr')
            if not rows: return {}
            
            range_list = []
            for r in rows:
                txt = r.get_text()
                if "小於" in txt or "~" in txt:
                    headers = r.find_all(['th', 'td'])
                    for h in headers:
                        t = h.get_text(strip=True)
                        lower = -1
                        if "小於" in t: lower = 0
                        else:
                            nums = re.findall(r'\d+', t)
                            if nums: lower = int(nums[0])
                        if lower != -1: range_list.append({'lower': lower})
                    break
            
            if not range_list: return {}

            result = {}
            for row in rows:
                cells = row.find_all(['td', 'th'])
                if len(cells) < 5: continue
                
                date_str = ""
                date_idx = -1
                for i, cell in enumerate(cells):
                    t = cell.get_text(strip=True)
                    match = re.search(r'(\d{8})', t)
                    if match:
                        date_str = match.group(1); date_idx = i; break
                
                if date_idx == -1: continue
                
                data_start = date_idx + 1
                row_data = []
                for i, r_info in enumerate(range_list):
                    idx = data_start + i
                    if idx < len(cells):
                        pct = self.clean_num(cells[idx].get_text())
                        row_data.append({'lower': r_info['lower'], 'pct': pct})
                
                if row_data: result[date_str] = row_data
            return result
        except (AttributeError, IndexError, TypeError, ValueError):
            return {}

    def calc_from_prior(self, data_list, threshold):
        ppl = 0; shares = 0; total_s = 0
        for item in data_list:
            total_s += item['shares']
            lower = 0
            nums = re.findall(r'\d+', item['range'].replace(',', ''))
            if nums: 
                val = int(nums[0])
                if "股" in item['range']: lower = 0
                else: lower = 1 if val==1 else val 

            if lower >= threshold:
                ppl += item['ppl']; shares += item['shares']
        pct = 0.0
        if total_s > 0: pct = round(shares / total_s * 100, 2)
        return {'ppl': int(ppl), 'pct': pct}

    def calc_from_graded(self, data_list, threshold):
        total_pct = 0.0
        for item in data_list:
            if item['lower'] >= threshold:
                total_pct += item['pct']
        return round(total_pct, 2)

    def scrape_stock_data(self, stock_id):
        driver = None
        current_stock_name = ""
        final_data = []

        try:
            # === 0. 抓取股票名稱 ===
            current_stock_name = self.get_stock_name_moneydj(stock_id)
            if not current_stock_name:
                current_stock_name = f"股票_{stock_id}"

            print(f"  -> 正在初始化瀏覽器... [{current_stock_name}]")
            chrome_options = Options()
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--log-level=3")
            chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64)")
            if self.settings.get("headless", True):
                chrome_options.add_argument("--headless=new")

            # Selenium Manager 會自動尋找與 Chrome 相容的驅動程式。
            driver = webdriver.Chrome(service=Service(), options=chrome_options)
            wait = WebDriverWait(driver, 20)
            
            # === 1. 主表 ===
            print("  -> Step 1/4: 抓取主歷史表...")
            driver.get(f"https://norway.twsthr.info/StockHolders.aspx?Stock={stock_id}")
            wait.until(EC.presence_of_element_located((By.ID, "Details")))
            
            main_history = self.parse_main_history(driver.find_element(By.ID, "Details"))
            if not main_history:
                raise ValueError("主歷史表沒有解析到有效資料，網站欄位可能已更新")
            
            # === 2. 前期比較 ===
            print("  -> Step 2/4: 抓取前期比較...")
            prior_data_map = {}
            try:
                tab_btn = driver.find_element(By.ID, "li2")
                driver.execute_script("arguments[0].click();", tab_btn)
                wait.until(EC.presence_of_element_located((By.XPATH, "//div[@id='D2']//td[contains(text(), '1-999')]")))
                time.sleep(1)
                
                d2_html = driver.find_element(By.ID, "D2").get_attribute('outerHTML')
                soup = BeautifulSoup(d2_html, 'html.parser')
                
                for tbl in soup.find_all('table'):
                    txt = tbl.get_text()
                    if "1-999" in txt and "400-600" in txt:
                        res = self.parse_prior_table_fixed(tbl)
                        if res: prior_data_map = res; break
            except Exception as e:
                print(f"  -> 前期比較抓取失敗: {str(e)}")

            # === 3. 分級比例 ===
            print("  -> Step 3/4: 抓取分級比例...")
            graded_pct_map = {}
            try:
                tab_btn = driver.find_element(By.ID, "li3")
                driver.execute_script("arguments[0].click();", tab_btn)
                wait.until(EC.presence_of_element_located((By.XPATH, "//div[@id='D3']//*[contains(text(), '小於') or contains(text(), '1~5')]")))
                time.sleep(1.5)
                
                d3_html = driver.find_element(By.ID, "D3").get_attribute('outerHTML')
                soup = BeautifulSoup(d3_html, 'html.parser')
                
                for tbl in soup.find_all('table'):
                    txt = tbl.get_text()
                    if "小於" in txt and "1~5" in txt:
                        res = self.parse_graded_table_fixed(tbl)
                        if res: graded_pct_map = res; break
            except Exception as e:
                print(f"  -> 分級比例抓取失敗: {str(e)}")

            # === 4. 融合數據 ===
            print("  -> Step 4/4: 數據融合運算中...")
            for row in main_history:
                date_str = row['date']
                price = row['price']
                threshold = self.calculate_bengo_threshold(price)
                
                major_ppl = row['raw_400_ppl']
                major_pct = row['raw_400_pct']
                note = ""
                
                if threshold < 400:
                    if date_str in prior_data_map:
                        stats = self.calc_from_prior(prior_data_map[date_str], threshold)
                        if stats['ppl'] > 0:
                            major_ppl = stats['ppl']; major_pct = stats['pct']
                            note = f"✅ 詳細級距修正(>{threshold})"
                        else:
                            if date_str in graded_pct_map:
                                corrected_pct = self.calc_from_graded(graded_pct_map[date_str], threshold)
                                if corrected_pct > 0:
                                    major_pct = corrected_pct; note = f"✅ 比例修正(>{threshold}), 人數僅>400"
                                else: note = "⚠️資料受限(僅>400)"
                            else: note = "⚠️資料受限(僅>400)"
                    elif date_str in graded_pct_map:
                        corrected_pct = self.calc_from_graded(graded_pct_map[date_str], threshold)
                        if corrected_pct > 0:
                            major_pct = corrected_pct; note = f"✅ 比例修正(>{threshold}), 人數僅>400"
                        else: note = "⚠️資料受限(僅>400)"
                    else: note = "⚠️資料受限(僅>400)"

                row['threshold_str'] = f"> {threshold}"
                row['major_ppl'] = major_ppl
                row['major_pct'] = major_pct
                row['note'] = note
                final_data.append(row)

        except Exception as e:
            print(f"  -> ❌ 執行期間發生錯誤: {str(e)}")
            print(traceback.format_exc())
        finally:
            if driver:
                driver.quit()
                print("  -> 瀏覽器已關閉。")

        return current_stock_name, final_data


# ==========================================
# 3. 本地儲存與同步至 Nuxt.js 網站 API
# ==========================================
def build_payload(stock_id, stock_name, history_data):
    stock_id = validate_stock_id(stock_id)
    if not isinstance(history_data, list) or not history_data:
        raise ValueError("history 必須包含至少一筆歷史資料")
    valid_rows = []
    for row in history_data:
        if not isinstance(row, dict) or not re.fullmatch(r"\d{8}", str(row.get("date", ""))):
            continue
        if float(row.get("price") or 0) <= 0:
            continue
        valid_rows.append(row)
    if not valid_rows:
        raise ValueError("history 沒有有效的 YYYYMMDD 日期及正數價格")
    return {
        "stock_id": stock_id,
        "stock_name": str(stock_name or f"股票_{stock_id}").strip(),
        "update_time": datetime.now().astimezone().isoformat(timespec="seconds"),
        "dashboard_url": DASHBOARD_URL,
        "history": valid_rows,
    }


def upload_payload(payload, session=None, api_url=UPLOAD_API_URL):
    client = session or create_http_session()
    response = client.post(api_url, json=payload, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    try:
        result = response.json()
    except requests.exceptions.JSONDecodeError as exc:
        raise RuntimeError("網站回應不是有效 JSON") from exc
    if not result.get("success"):
        raise RuntimeError(result.get("message") or "網站拒絕同步資料")
    return result


def export_and_sync_data(stock_id, stock_name, history_data, session=None):
    try:
        payload = build_payload(stock_id, stock_name, history_data)
    except (TypeError, ValueError) as exc:
        print(f"  -> ❌ 資料驗證失敗: {exc}")
        return False

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = re.sub(r'[<>:"/\\|?*]+', '_', payload["stock_name"])[:40]
    filename = f"{payload['stock_id']}_{safe_name}_{timestamp}.json"
    save_dir = "Bengo_JSON_Backups"
    os.makedirs(save_dir, exist_ok=True)
    filepath = os.path.join(save_dir, filename)

    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(payload, f, ensure_ascii=False, indent=4)
        print(f"  -> ✅ 本地儲存成功: {filepath}")
    except OSError as exc:
        print(f"  -> ❌ 本地儲存失敗: {exc}")
        return False

    try:
        result = upload_payload(payload, session=session)
        print(f"  -> 🎉 網站資料庫同步成功！寫入 {result.get('count', len(payload['history']))} 筆，儲存位置：{result.get('storage', 'database')}")
        print(f"  -> 🌐 {DASHBOARD_URL}")
        return True
    except (requests.exceptions.RequestException, RuntimeError) as exc:
        print(f"  -> ❌ 網站同步失敗，本地備份仍已保留: {exc}")
        return False


# ==========================================
# 4. 主程式執行迴圈
# ==========================================
def main():
    configure_working_directory()
    settings = load_settings()
    print("=======================================")
    print("   Bengo 籌碼自動抓取與同步系統 (590bbs版) ")
    print("=======================================")
    print(f"目前網站: {DASHBOARD_URL}")
    print(f"同步 API: {UPLOAD_API_URL}\n")
    
    stock_ids = read_stock_ids()
    if not stock_ids:
        return 2
        
    total_stocks = len(stock_ids)
    print(f"共讀取到 {total_stocks} 檔股票準備處理。\n")
    
    session = create_http_session()
    scraper = BengoScraper(settings=settings, session=session)
    succeeded = 0
    failed = 0

    for index, stock_id in enumerate(stock_ids):
        current_step = index + 1
        print(f"\n[{current_step}/{total_stocks}] 開始處理股票代號: {stock_id}")
        
        try:
            stock_name, history_data = scraper.scrape_stock_data(stock_id)
            
            if history_data and len(history_data) > 0:
                if export_and_sync_data(stock_id, stock_name, history_data, session=session):
                    succeeded += 1
                else:
                    failed += 1
            else:
                print(f"  -> ⚠️ 警告: 未取得 {stock_id} 的有效歷史資料，略過儲存與同步。")
                failed += 1
                
        except Exception as e:
            print(f"  -> ❌ 處理 {stock_id} 時發生最外層異常: {e}")
            failed += 1
            
        if current_step < total_stocks:
            wait_time = random.randint(settings["minimum_wait_seconds"], settings["maximum_wait_seconds"])
            print(f"  -> ⏳ 隨機等待 {wait_time} 秒以防被伺服器阻擋...")
            for remaining in range(wait_time, 0, -1):
                print(f"\r  -> 倒數 {remaining} 秒... ", end="", flush=True)
                time.sleep(1)
            print("\r" + " " * 30 + "\r", end="", flush=True)
            print("-" * 40)
            
    print(f"\n處理完成：成功 {succeeded} 檔，失敗 {failed} 檔。")
    print(f"目前網站：{DASHBOARD_URL}")
    if settings.get("open_dashboard_when_finished"):
        webbrowser.open(DASHBOARD_URL)
    return 0 if failed == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
