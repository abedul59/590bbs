import pandas as pd
import datetime
import os
import sys
import glob
import shutil
import requests
import time
import re
import zipfile
import urllib3
import traceback
import json
import fnmatch
import xlrd 

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.service import Service 

try:
    from webdriver_manager.chrome import ChromeDriverManager
    WDM_AVAILABLE = True
except ImportError:
    WDM_AVAILABLE = False

# 忽略 SSL 警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def get_app_dir():
    """回傳腳本或 PyInstaller 執行檔所在目錄。"""
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def normalize_api_key(value):
    """Normalize a configured API key without ever logging its contents."""
    if not isinstance(value, str):
        return ""

    key = value.strip()
    normalized = key.casefold().replace("_", " ").replace("-", " ")
    placeholders = {
        "your fred api key",
        "fred api key",
        "please enter your fred api key",
        "請填入您的 fred api key",
    }
    if not key or normalized in placeholders or "請填入" in normalized:
        return ""
    return key


def get_config_paths():
    """Return supported config locations in priority order."""
    directories = [get_app_dir(), os.getcwd()]
    filenames = [
        "macrowave_config.json",
        "macrowave_config.example.json",
        "macrowave_config.json.txt",
    ]
    paths = []
    for directory in directories:
        for filename in filenames:
            path = os.path.abspath(os.path.join(directory, filename))
            if path not in paths:
                paths.append(path)
    return paths


def get_config_value(config, names):
    """Read the first non-empty supported key name from a JSON object."""
    if not isinstance(config, dict):
        return ""
    for name in names:
        value = normalize_api_key(config.get(name))
        if value:
            return value
    return ""


def load_config():
    """讀取 Windows 環境變數或 EXE／啟動目錄旁的 JSON 設定。"""
    loaded_configs = []
    for config_path in get_config_paths():
        if not os.path.isfile(config_path):
            continue
        try:
            with open(config_path, 'r', encoding='utf-8-sig') as config_file:
                config = json.load(config_file)
            if not isinstance(config, dict):
                raise ValueError("JSON 最外層必須是物件")
            loaded_configs.append((config_path, config))
        except Exception as error:
            print(f"⚠️ 無法讀取 {config_path}: {error}")

    env_fred_key = normalize_api_key(os.environ.get("FRED_API_KEY"))
    env_upload_key = normalize_api_key(os.environ.get("MACROWAVE_API_KEY"))

    file_fred_key = ""
    file_upload_key = ""
    fred_source = ""
    upload_source = ""
    for config_path, config in loaded_configs:
        if not file_fred_key:
            file_fred_key = get_config_value(
                config, ("fred_api_key", "FRED_API_KEY", "fredApiKey", "fred_key")
            )
            if file_fred_key:
                fred_source = config_path
        if not file_upload_key:
            file_upload_key = get_config_value(
                config, ("upload_api_key", "MACROWAVE_API_KEY", "uploadApiKey")
            )
            if file_upload_key:
                upload_source = config_path

    return {
        "fred_api_key": env_fred_key or file_fred_key,
        "upload_api_key": env_upload_key or file_upload_key or "macrowave168",
        "fred_api_key_source": "Windows 環境變數 FRED_API_KEY" if env_fred_key else fred_source,
        "upload_api_key_source": "Windows 環境變數 MACROWAVE_API_KEY" if env_upload_key else upload_source,
        "config_paths": get_config_paths(),
    }


APP_CONFIG = load_config()

# ==========================================
# 共用日誌系統
# ==========================================
def log_msg(msg):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{now}] {msg}")

# ==========================================
# 0. 驅動程式自動檢測與下載
# ==========================================
def setup_driver():
    log_msg("=== 階段 0: 檢查與更新 ChromeDriver ===")
    if not WDM_AVAILABLE:
        log_msg("⚠️ 未安裝 webdriver-manager，將使用系統內建驅動。")
        return

    try:
        log_msg("正在連線伺服器檢測 Chrome 版本並下載匹配的驅動程式...")
        installed_path = ChromeDriverManager().install()
        
        if getattr(sys, 'frozen', False):
            base_path = os.path.dirname(sys.executable)
        else:
            base_path = os.path.dirname(os.path.abspath(__file__))
            
        target_path = os.path.join(base_path, "chromedriver.exe")
        shutil.copy2(installed_path, target_path)
        log_msg(f"✅ ChromeDriver 已就緒: {target_path}")
    except Exception as e:
        log_msg(f"❌ 驅動下載失敗，將使用系統預設設定: {e}")

# ==========================================
# 邏輯區塊 A: 債券與原物料
# ==========================================
class MacroWaveA_Logic:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'https://www.google.com/'
        }

    def get_us_bond_yields(self):
        urls = {'3M': 'https://www.cnyes.com/futures/html5chart/TB3MY.html', '10Y': 'https://www.cnyes.com/futures/html5chart/US10YY.html'}
        results = {}
        for key, url in urls.items():
            try:
                r = requests.get(url, headers=self.headers, verify=False, timeout=10)
                df = pd.read_html(r.text)[0]
                results[key] = float(df.iloc[0][1])
            except: 
                results[key] = 0.0
        return results.get('3M', 0), results.get('10Y', 0)

    def get_crb_index(self):
        crb = "N/A"
        sources = [
            ("StockQ", 'https://www.stockq.org/index/CRB.php'),
            ("Business Insider", "https://markets.businessinsider.com/indices/thomson-reuters-corecommodity-crb-index"),
            ("MarketWatch", "https://www.marketwatch.com/investing/index/crb")
        ]
        for name, url in sources:
            try:
                r = requests.get(url, headers=self.headers, timeout=10)
                matches = re.findall(r'[>"\s](2\d{2}\.\d{2}|3\d{2}\.\d{2})[<"\s]', r.text)
                if matches:
                    crb = matches[0]
                    log_msg(f"CRB 抓取成功 ({name}): {crb}")
                    break
            except: pass
        return crb, "N/A", "N/A"

    def run(self):
        b3, b10 = self.get_us_bond_yields()
        c_idx, c_h, c_y = self.get_crb_index()
        try: spread = round(b10 - b3, 4)
        except: spread = 0
        return {
            "Date": datetime.datetime.now().strftime("%Y-%m-%d"),
            "US_3M": b3, "US_10Y": b10, "Spread_3M_10Y": spread,
            "CRB_Index": c_idx, "CRB_HalfYear": c_h, "CRB_OneYear": c_y
        }

# ==========================================
# 邏輯區塊 B & C: 總經指標
# ==========================================
class MacroWaveBC_Logic:
    def __init__(self):
        self.fred_key = APP_CONFIG["fred_api_key"]
        try:
            if not self.fred_key:
                raise ValueError("尚未設定 FRED API Key")
            from fredapi import Fred
            self.fred = Fred(api_key=self.fred_key)
        except (ImportError, ValueError):
            self.fred = None

        if getattr(sys, 'frozen', False):
            self.base_dir = os.path.dirname(sys.executable)
        else:
            self.base_dir = os.path.dirname(os.path.abspath(__file__))
            
        self.temp_dir = os.path.join(self.base_dir, "TempDownloads")
        self.dirs = {
            "recession": os.path.join(self.base_dir, "RecessPossi"),
            "m1b": os.path.join(self.base_dir, "M1b"),
            "mv": os.path.join(self.base_dir, "MarketValue")
        }
        
        if not os.path.exists(self.temp_dir): os.makedirs(self.temp_dir)
        for d in self.dirs.values():
            if not os.path.exists(d): os.makedirs(d)

    def get_driver(self):
        opts = Options()
        # 移除 Headless，使用真實視窗繞過防爬蟲
        # opts.add_argument('--headless=new')
        opts.add_argument('--disable-gpu')
        opts.add_argument("--disable-blink-features=AutomationControlled") 
        opts.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36")
        opts.add_argument('--no-sandbox')
        opts.add_argument('--disable-dev-shm-usage')
        opts.add_argument('--disable-infobars')
        opts.add_experimental_option("excludeSwitches", ["enable-automation"])
        opts.add_experimental_option('useAutomationExtension', False)
        opts.add_experimental_option("prefs", {
            "download.default_directory": self.temp_dir,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True,
            "safebrowsing.disable_download_protection": True,
            "profile.default_content_setting_values.automatic_downloads": 1
        })
        
        driver_path = os.path.join(self.base_dir, "chromedriver.exe")
        if os.path.exists(driver_path):
            try:
                service = Service(executable_path=driver_path)
                driver = webdriver.Chrome(service=service, options=opts)
            except TypeError:
                driver = webdriver.Chrome(executable_path=driver_path, options=opts)
        else:
            driver = webdriver.Chrome(options=opts)

        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        })

        driver.set_page_load_timeout(30) 
        driver.set_script_timeout(30)
        return driver

    def clear_temp(self):
        for f in os.listdir(self.temp_dir):
            try: os.remove(os.path.join(self.temp_dir, f))
            except: pass

    def get_local_fallback(self, key):
        folder = self.dirs.get(key)
        pattern = "*.xls*"
        files = glob.glob(os.path.join(folder, pattern))
        if not files: return None
        latest = max(files, key=os.path.getmtime)
        log_msg(f"[{key}] 讀取備援: {os.path.basename(latest)}")
        return latest

    def backup_file(self, src, key):
        try:
            dst = self.dirs.get(key)
            shutil.copy2(src, os.path.join(dst, os.path.basename(src)))
        except: pass

    # --- Market Value ---
    def get_market_value(self):
        path1 = self.temp_dir
        current_date = datetime.datetime.now()
        current_year = current_date.year      
        current_month = current_date.month    
        
        business_days_count = 0
        seventh_business_day_date = 7 
        for day in range(1, 32):
            try: check_date = datetime.date(current_year, current_month, day)
            except ValueError: break
            if check_date.weekday() < 5: business_days_count += 1
            if business_days_count == 7:
                seventh_business_day_date = day
                break

        if current_date.day >= seventh_business_day_date:
            target_month_int = current_month - 1
            target_western_year = current_year
        else:
            target_month_int = current_month - 2
            target_western_year = current_year

        if target_month_int == 0:        
            target_month_int = 12
            target_western_year = current_year - 1
        elif target_month_int == -1:     
            target_month_int = 11
            target_western_year = current_year - 1

        target_col_index = target_month_int + 1

        for f_nameD in os.listdir(path1):
            if fnmatch.fnmatch(f_nameD, '*.zip') or fnmatch.fnmatch(f_nameD, '*.xls'):
                os.remove(os.path.join(path1, f_nameD))
        for f_nameZ in os.listdir(path1):
            if fnmatch.fnmatch(f_nameZ, '*.crdownload'):
                os.remove(os.path.join(path1, f_nameZ))

        aUrl = ('https://www.twse.com.tw/zh/trading/statistics/index02.html')
        driver = None
        success = False
        target_file = None
        
        try:
            driver = self.get_driver()
            driver.get(aUrl)
            wait = WebDriverWait(driver, 20)
            wait.until(EC.presence_of_element_located((By.NAME, "yy")))
            
            select_element = driver.find_element(By.NAME, "yy")
            select_object = Select(select_element)
            select_object.select_by_value(str(target_western_year))
            
            try:
                submit_btn = wait.until(EC.presence_of_element_located((By.XPATH, "//*[contains(@class, 'search') and text()='查詢']")))
                driver.execute_script("arguments[0].scrollIntoView();", submit_btn)
                time.sleep(1) 
                try: submit_btn.click()
                except: driver.execute_script("arguments[0].click();", submit_btn)
            except: pass
            
            time.sleep(3) 
            wait.until(EC.presence_of_element_located((By.ID, "reports")))
            
            try:
                xpath_str = f"//*[@id='reports']//table/tbody/tr[1]/td[{target_col_index}]/a"
                element = wait.until(EC.element_to_be_clickable((By.XPATH, xpath_str)))
                element.click()
            except:
                xpath_backup = f"//table/tbody/tr[1]/td[{target_col_index}]/a" 
                try: driver.execute_script("arguments[0].click();", driver.find_element(By.XPATH, xpath_backup))
                except: pass

            download_complete = False
            target_zip = None
            for i in range(30):
                time.sleep(1)
                files = os.listdir(path1)
                for f in files:
                    if f.endswith('.zip'):
                        target_zip = f
                        download_complete = True
                        break
                if download_complete: break
            
            if download_complete:
                with zipfile.ZipFile(os.path.join(path1, target_zip), 'r') as zf:
                    zf.extractall(path1)
                time.sleep(2) 
                os.remove(os.path.join(path1, target_zip))
                
                xls_files = [f for f in os.listdir(path1) if f.endswith('.xls')]
                if xls_files:
                    target_file = os.path.join(path1, xls_files[0])
                    self.backup_file(target_file, "mv")
                    success = True
        except Exception as e:
            log_msg(f"市值執行錯誤: {e}")
        finally:
            if driver:
                try: driver.quit()
                except: pass

        if not success:
            target_file = self.get_local_fallback("mv")

        if target_file:
            try:
                dfs = pd.read_excel(target_file)
                lastone = dfs.tail(7)
                MVTime = str(lastone.iloc[0][0])
                try: MVNum = float(lastone.iloc[0][5])
                except: MVNum = 0.0
                return MVTime, MVNum
            except Exception as e:
                log_msg(f"市值 Excel 讀取錯誤: {e}")
        return "N/A", 0

    # --- M1b ---
    def get_m1b(self):
        self.clear_temp()
        success = False
        target_file = None
        driver = None
        try:
            driver = self.get_driver()
            driver.get('https://www.cbc.gov.tw/tw/cp-523-975-DEE11-1.html')
            time.sleep(3)
            driver.find_element(By.XPATH, '//*[@id="center"]/div[2]/div[3]/ul/li/a[3]').click()
            time.sleep(5)
            xls = [f for f in os.listdir(self.temp_dir) if f.endswith('xls') or f.endswith('xlsx')][0]
            target_file = os.path.join(self.temp_dir, xls)
            self.backup_file(target_file, "m1b")
            success = True
            driver.quit()
        except: 
            try: driver.quit()
            except: pass

        if not success: target_file = self.get_local_fallback("m1b")

        if target_file:
            try:
                df = pd.read_excel(target_file)
                df.iloc[:, 13] = pd.to_numeric(df.iloc[:, 13], errors='coerce')
                df.iloc[:, 14] = pd.to_numeric(df.iloc[:, 14], errors='coerce')
                valid_df = df.dropna(subset=[df.columns[13]])
                valid_rows = []
                for idx, row in valid_df.iterrows():
                    if "註" not in str(row.iloc[0]) and len(str(row.iloc[0])) < 15:
                        valid_rows.append(row)
                if valid_rows:
                    last = valid_rows[-1]
                    return str(last.iloc[0]), str(last.iloc[14]), float(last.iloc[13])
            except Exception as e: pass
        return "N/A", "N/A", 0

    # --- China PMI ---
    def get_china_pmi(self):
        val = "N/A"
        date_str = datetime.datetime.now().strftime("%Y-%m")
        driver = None
        try:
            log_msg("爬取中國 PMI (Google News)...")
            driver = self.get_driver()
            url = "https://www.google.com/search?q=China+Manufacturing+PMI+latest&gl=us&hl=en&tbm=nws"
            driver.get(url)
            wait = WebDriverWait(driver, 15)
            wait.until(EC.presence_of_element_located((By.ID, "search")))
            body_text = driver.find_element(By.TAG_NAME, "body").text
            matches = re.findall(r'(?:China|PMI).*?([45]\d\.\d)', body_text)
            if matches:
                val = matches[0]
                date_str += " (News)"
                log_msg(f"PMI 抓取成功: {val}")
        except Exception as e: 
            log_msg(f"China PMI 抓取失敗: {e}")
        finally:
            if driver:
                try: driver.quit()
                except: pass
        return val, date_str

    # --- 衰退機率 (還原您的 GUI 版本邏輯) ---
    def get_recession_prob(self):
        self.clear_temp()
        success = False
        target_file = None
        driver = None
        try:
            log_msg("爬取衰退機率...")
            driver = self.get_driver()
            driver.get('https://www.newyorkfed.org/research/capital_markets/ycfaq.html#/overview')
            
            time.sleep(5) 
            
            try:
                xpath = '/html/body/div[1]/app-root/div/app-overview/div[1]/div[7]/a[2]'
                driver.find_element(By.XPATH, xpath).click()
            except Exception as e:
                try:
                    btn = driver.find_element(By.XPATH, '/html/body/div[1]/app-root/div/app-overview/div[1]/div[7]/a[2]')
                    driver.execute_script("arguments[0].click();", btn)
                except: pass

            time.sleep(5)
            
            files = [f for f in os.listdir(self.temp_dir) if f.endswith('xls') or f.endswith('xlsx')]
            if files:
                target_file = os.path.join(self.temp_dir, files[0])
                self.backup_file(target_file, "recession")
                success = True
        except Exception as e: 
            log_msg(f"衰退機率抓取錯誤: {e}")
        finally:
            if driver:
                try: driver.quit()
                except: pass
        
        if not success: 
            target_file = self.get_local_fallback("recession")
        
        if target_file:
            try:
                df = pd.read_excel(target_file)
                last = df.tail(1)
                try:
                    date_val = str(last.iloc[0][0])[:10]
                    prob_val = f"{round(float(last.iloc[0][5])*100, 2)}%" 
                    return date_val, prob_val
                except Exception as ex:
                    return str(last.iloc[0][0])[:10], "Error"
            except Exception as e: pass
        return "N/A", "N/A"

    def get_us_li(self):
        val = "N/A"
        date_str = datetime.datetime.now().strftime("%Y-%m")
        driver = None
        try:
            log_msg("爬取美國領先指標 (Google News)...")
            driver = self.get_driver()
            url = "https://www.google.com/search?q=US+Conference+Board+Leading+Economic+Index+latest&gl=us&hl=en&tbm=nws"
            driver.get(url)
            wait = WebDriverWait(driver, 15)
            wait.until(EC.presence_of_element_located((By.ID, "search")))
            body_text = driver.find_element(By.TAG_NAME, "body").text
            matches = re.findall(r'(?:LEI|Leading Economic Index).*?(?:to|at)\s*((?:9\d|1\d{2})\.\d)', body_text, re.IGNORECASE)
            if not matches:
                matches = re.findall(r'(?:LEI|Leading Economic Index).*?((?:9\d|1\d{2})\.\d)', body_text, re.IGNORECASE)
            if matches:
                val = matches[0]
                date_str += " (News)"
        except Exception as e: 
            log_msg(f"LEI 抓取失敗: {e}")
        finally:
            if driver:
                try: driver.quit() 
                except: pass
        return val, date_str
    
    def get_unrate(self):
        if not self.fred: return "N/A"
        try: return str(self.fred.get_series('UNRATE').iloc[-1])
        except: return "N/A"

    def get_durable(self):
        if not self.fred: return "N/A", "N/A"
        try:
            d = self.fred.get_series('DGORDER')
            y1 = (d.iloc[-1]-d.iloc[-13])/d.iloc[-13]*100
            y2 = (d.iloc[-2]-d.iloc[-14])/d.iloc[-14]*100
            return f"{round(y1,2)}%", f"{round(y2,2)}%"
        except: return "N/A", "N/A"

    def get_michigan(self):
        driver = None
        try:
            driver = self.get_driver()
            driver.get('https://www.moneydj.com/funddj/yl/BFRK01.djhtm?a=EI020007')
            time.sleep(3)
            n = driver.find_element(By.XPATH, '//*[@id="CURVE"]/div[2]/div[3]/div[3]/div[2]/div/span').text
            driver.quit()
            return datetime.datetime.now().strftime("%Y-%m"), n
        except: 
            try: driver.quit()
            except: pass
            return "N/A", "N/A"

    def run_b(self):
        rd, rp = self.get_recession_prob() 
        mt, my, mn = self.get_m1b()
        mvt, mvn = self.get_market_value()
        try: ratio = round((mvn/100)/mn, 2) if mn!=0 else 0
        except: ratio = 0
        return {"Recession_Date":rd, "Recession_Prob":rp, "M1b_Date":mt, "M1b_YoY":my, "M1b_Num":mn, "MV_Date":mvt, "MV_Num":mvn, "MV_Ratio":ratio}

    def run_c(self):
        li_v, li_t = self.get_us_li()
        ur = self.get_unrate()
        mc_t, mc_v = self.get_michigan()
        dy1, dy2 = self.get_durable()
        pmi_v, pmi_t = self.get_china_pmi()
        return {"Unemployment":ur, "Leading_Index_Date":li_t, "Leading_Index":li_v, "Michigan_Date":mc_t, "Michigan_Index":mc_v, "Durable_YoY_New":dy1, "Durable_YoY_Old":dy2, "China_PMI_Date":pmi_t, "China_PMI":pmi_v}

# ==========================================
# 邏輯區塊 D: 美日利差
# ==========================================
class MacroWaveD_Logic:
    def __init__(self):
        self.headers = {'User-Agent': 'Mozilla/5.0'}

    def get_us_10y(self):
        try: return MacroWaveA_Logic().get_us_bond_yields()[1]
        except: return 0.0

    def get_jp_10y(self):
        jp10y = 0.0
        try:
            url = "https://www.cnyes.com/futures/html5chart/JP10YY.html"
            r = requests.get(url, headers=self.headers, verify=False, timeout=10)
            df = pd.read_html(r.text)[0]
            val = float(df.iloc[0][1])
            if val > 0: return val
        except: pass

        try:
            url = "https://tradingeconomics.com/japan/government-bond-yield"
            r = requests.get(url, headers=self.headers, timeout=10)
            m = re.search(r'data-value="(\d+\.\d+)"', r.text)
            if m: return float(m.group(1))
        except: pass

        return jp10y

    def run(self):
        us = self.get_us_10y()
        jp = self.get_jp_10y()
        spread = round(us - jp, 4)
        return {"US_10Y": us, "JP_10Y": jp, "Spread": spread}

# ==========================================
# 邏輯區塊 E: 貴金屬
# ==========================================
class MacroWaveE_Logic:
    def __init__(self):
        self.headers = {'User-Agent': 'Mozilla/5.0'}
        self.codes = {"黃金 (Gold)": "GC", "白銀 (Silver)": "SI", "銅 (Copper)": "HG", "錫 (Tin)": "SND", "鎳 (Nickel)": "NID"}

    def get_data(self):
        results = []
        for name, code in self.codes.items():
            try:
                url = f"https://stock2.finance.sina.com.cn/futures/api/jsonp.php//GlobalFuturesService.getGlobalFuturesDailyKLine?symbol={code}"
                r = requests.get(url, headers=self.headers, timeout=10)
                raw = r.text
                start = raw.find('([')
                end = raw.find('])')
                if start != -1 and end != -1:
                    data = json.loads(raw[start+1:end+1])
                    df = pd.DataFrame(data)
                    recent = df.tail(125)
                    max_high = float(recent['high'].max())
                    curr_price = float(recent.iloc[-1]['close'])
                    drop = (max_high - curr_price) / max_high * 100
                    results.append({"name": name, "current": curr_price, "high_6m": max_high, "drop_pct": round(drop, 2), "date": recent.iloc[-1]['date']})
                else:
                    results.append({"name": name, "current": 0, "high_6m": 0, "drop_pct": 0, "date": "N/A"})
            except:
                results.append({"name": name, "current": 0, "high_6m": 0, "drop_pct": 0, "date": "Error"})
        return results

# ==========================================
# 邏輯區塊 Currency: 匯率 
# ==========================================
class MacroWaveCurrency_Logic:
    def get_data(self):
        results = []
        tickers = {"美元指數 (DXY)": "DX-Y.NYB", "美元/日圓 (USD/JPY)": "JPY=X", "美元/人民幣 (USD/CNY)": "CNY=X", "日圓/台幣 (JPY/TWD)": "JPYTWD=X", "美元/台幣 (USD/TWD)": "USDTWD=X"}
        headers = {'User-Agent': 'Mozilla/5.0'}
        for name, ticker in tickers.items():
            try:
                url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?range=6mo&interval=1d"
                r = requests.get(url, headers=headers, timeout=10)
                quote = r.json()['chart']['result'][0]['indicators']['quote'][0]
                closes = [x for x in quote['close'] if x is not None]
                if closes:
                    current = closes[-1]
                    high_6m = max([x for x in quote['high'] if x is not None])
                    low_6m = min([x for x in quote['low'] if x is not None])
                    results.append({"name": name, "current": round(current, 4), "high_6m": round(high_6m, 4), "low_6m": round(low_6m, 4), "diff_high": round((current - high_6m)/high_6m*100, 2), "diff_low": round((current - low_6m)/low_6m*100, 2)})
                else:
                    results.append({"name": name, "current": 0, "diff_high": 0, "diff_low": 0})
            except:
                results.append({"name": name, "current": 0, "diff_high": 0, "diff_low": 0})
        return results

# ==========================================
# 邏輯區塊 GlobalMarket: 全球股市位階 
# ==========================================
class MacroWaveGlobalMarket_Logic:
    def get_data(self):
        results = []
        indices = {"台灣加權指數": "^TWII", "日經 225": "^N225", "道瓊工業指數": "^DJI", "標普 500": "^GSPC", "那斯達克": "^IXIC", "費城半導體": "^SOX", "上證指數": "000001.SS"}
        headers = {'User-Agent': 'Mozilla/5.0'}
        for name, ticker in indices.items():
            try:
                url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?range=5y&interval=1d"
                r = requests.get(url, headers=headers, timeout=15)
                data = r.json()
                if not data['chart']['result']: continue
                result = data['chart']['result'][0]
                df = pd.DataFrame({'ts': result['timestamp'], 'high': result['indicators']['quote'][0]['high'], 'low': result['indicators']['quote'][0]['low'], 'close': result['indicators']['quote'][0]['close']})
                df['date'] = pd.to_datetime(df['ts'], unit='s')
                df = df.dropna()
                if df.empty: continue
                current_price = df['close'].iloc[-1]
                current_date = df['date'].iloc[-1]
                
                row_data = {"name": name, "current": round(current_price, 2)}
                for label, days in {"6M": 180, "1Y": 365, "3Y": 1095}.items():
                    period_df = df[df['date'] >= current_date - datetime.timedelta(days=days)]
                    if not period_df.empty:
                        h, l = period_df['high'].max(), period_df['low'].min()
                        row_data.update({f"{label}_High": round(h, 2), f"{label}_High_Diff": round((current_price - h)/h*100, 2), f"{label}_Low": round(l, 2), f"{label}_Low_Diff": round((current_price - l)/l*100, 2)})
                    else:
                        row_data.update({f"{label}_High": 0, f"{label}_High_Diff": 0, f"{label}_Low": 0, f"{label}_Low_Diff": 0})
                results.append(row_data)
            except: pass
        return results

# ==========================================
# 邏輯區塊 F: Mark 17 (已完全還原自 GUI 成功版本)
# ==========================================
class MacroWaveMark17_Logic:
    def __init__(self):
        self.fred_key = APP_CONFIG["fred_api_key"]
        try:
            if not self.fred_key:
                raise ValueError("尚未設定 FRED API Key")
            from fredapi import Fred
            self.fred = Fred(api_key=self.fred_key)
        except:
            self.fred = None
        self.headers = {'User-Agent': 'Mozilla/5.0'}
        
        if getattr(sys, 'frozen', False):
            self.base_dir = os.path.dirname(sys.executable)
        else:
            self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.temp_dir = os.path.join(self.base_dir, "TempDownloads")

    def get_driver(self):
        opts = Options()
        opts.add_argument('--disable-gpu')
        opts.add_argument("--disable-blink-features=AutomationControlled")
        opts.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36")
        opts.add_argument('--no-sandbox')
        opts.add_argument('--disable-dev-shm-usage')
        opts.add_argument('--disable-infobars')
        opts.add_experimental_option("excludeSwitches", ["enable-automation"])
        opts.add_experimental_option('useAutomationExtension', False)
        
        if getattr(sys, 'frozen', False):
            base_path = os.path.dirname(sys.executable)
        else:
            base_path = os.path.dirname(os.path.abspath(__file__))
            
        driver_path = os.path.join(base_path, "chromedriver.exe")
        
        if os.path.exists(driver_path):
            try:
                service = Service(executable_path=driver_path)
                driver = webdriver.Chrome(service=service, options=opts)
            except TypeError:
                driver = webdriver.Chrome(executable_path=driver_path, options=opts)
        else:
            driver = webdriver.Chrome(options=opts)
            
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        })
        driver.set_page_load_timeout(30)
        return driver

    def get_us_pmi_from_news(self):
        driver = None
        history = []
        try:
            log_msg("啟動 Selenium 抓取 Google News (US PMI)...")
            driver = self.get_driver()
            url = "https://www.google.com/search?q=US+ISM+Manufacturing+PMI+latest&gl=us&hl=en&tbm=nws"
            driver.get(url)
            wait = WebDriverWait(driver, 10)
            wait.until(EC.presence_of_element_located((By.ID, "search")))
            body_text = driver.find_element(By.TAG_NAME, "body").text
            matches = re.findall(r'(?:ISM|PMI).*?([45]\d\.\d)', body_text)
            if matches:
                latest_val = float(matches[0])
                log_msg(f"Google News PMI 抓取數值: {latest_val}")
                history.append(latest_val)
            else:
                log_msg("Google News 未找到 PMI 數值")
            return history
        except Exception as e:
            log_msg(f"Google News 抓取失敗: {e}")
            return []
        finally:
            if driver:
                try: driver.quit() 
                except: pass

    def get_us_inflation_gap(self):
        if not self.fred: return None
        try:
            log_msg("抓取美國 PPI & CPI (FRED)...")
            ppi_series = self.fred.get_series('PPIACO').tail(13)
            cpi_series = self.fred.get_series('CPIAUCSL').tail(13)
            ppi_yoy = (ppi_series.iloc[-1] - ppi_series.iloc[-13]) / ppi_series.iloc[-13] * 100
            cpi_yoy = (cpi_series.iloc[-1] - cpi_series.iloc[-13]) / cpi_series.iloc[-13] * 100
            gap = ppi_yoy - cpi_yoy
            log_msg(f"Gap: {gap:.2f}%")
            return gap
        except Exception as e:
            log_msg(f"Inflation Gap 失敗: {e}")
            return None

    def get_us_bei(self):
        if not self.fred: return None
        try:
            log_msg("抓取美國 BEI (FRED)...")
            bei = self.fred.get_series('T10YIE').iloc[-1]
            return float(bei)
        except Exception as e:
            log_msg(f"BEI 抓取失敗: {e}")
            return None

    def calculate_score(self, data_a, data_b, data_c):
        score = 0
        details = []

        pmi_hist = self.get_us_pmi_from_news()
        if pmi_hist:
            latest_pmi = pmi_hist[0]
            if latest_pmi < 50:
                score += 1
                details.append((f"PMI < 50 (最新: {latest_pmi})", "是", "+1"))
                details.append(("PMI < 50 (連續6月)", "資料不足", "0"))
            else:
                details.append((f"PMI < 50 (最新: {latest_pmi})", "否", "0"))
                details.append(("PMI < 50 (連續6月)", "否", "0"))
            details.append(("PMI 來源", "Google News", "(僅參考)"))
        else:
            details.append(("PMI 數據", "N/A", "0"))
            details.append(("PMI 數據", "N/A", "0"))

        try:
            m1b_yoy = float(data_b.get('M1b_YoY', 0))
            if m1b_yoy < 0:
                score += 3; details.append(("M1B 轉負", f"{m1b_yoy}%", "+3"))
            else: details.append(("M1B 轉負", f"{m1b_yoy}%", "0"))
        except: details.append(("M1B", "Error", "0"))

        try:
            mv_ratio = float(data_b.get('MV_Ratio', 0))
            if mv_ratio > 2:
                score += 2; details.append(("市值貨幣比 > 2", f"{mv_ratio}", "+2"))
            else: details.append(("市值貨幣比 > 2", f"{mv_ratio}", "0"))
        except: details.append(("市值貨幣比", "Error", "0"))

        try:
            spread = float(data_a.get('Spread_3M_10Y', 0))
            if spread < 0:
                score += 3; details.append(("殖利率倒掛", f"{spread}", "+3"))
            else: details.append(("殖利率倒掛", f"{spread}", "0"))
        except: details.append(("殖利率", "Error", "0"))

        try:
            rp_str = data_b.get('Recession_Prob', "0").replace('%', '')
            rp = float(rp_str)
            if rp > 20:
                score += 1; details.append(("衰退機率 > 20%", f"{rp}%", "+1"))
            else: details.append(("衰退機率 > 20%", f"{rp}%", "0"))
        except: details.append(("衰退機率", "Error", "0"))

        gap = self.get_us_inflation_gap()
        if gap is None:
            details.append(("PPI - CPI > 4%", "N/A (FRED)", "-"))
        elif gap > 4:
            score += 2; details.append(("PPI - CPI > 4%", f"{gap:.2f}%", "+2"))
        else: details.append(("PPI - CPI > 4%", f"{gap:.2f}%", "0"))

        bei = self.get_us_bei()
        if bei is None:
            details.append(("BEI > 2.5%", "N/A (FRED)", "-"))
        elif bei > 2.5:
            score += 1; details.append(("BEI > 2.5%", f"{bei:.2f}%", "+1"))
        else: details.append(("BEI > 2.5%", f"{bei:.2f}%", "0"))

        try:
            ur = float(data_c.get('Unemployment', 0))
            if ur > 4.5:
                score += 2; details.append(("失業率 > 4.5%", f"{ur}%", "+2"))
                details.append(("失業率 > 4%", f"{ur}%", "0 (已計入 > 4.5%)"))
            elif ur > 4:
                score += 1; details.append(("失業率 > 4%", f"{ur}%", "+1"))
                details.append(("失業率 > 4.5%", f"{ur}%", "0"))
            else:
                details.append(("失業率 > 4%", f"{ur}%", "0"))
                details.append(("失業率 > 4.5%", f"{ur}%", "0"))
        except: 
            details.extend([("失業率", "Error", "0"), ("失業率", "Error", "0")])

        return score, details

# ==========================================
# 邏輯區塊 G: JSON 生成器
# ==========================================
class MacroWaveJSON_Logic:
    def generate_json(self, data_a, data_b, data_c, data_d, data_e, data_currency, data_global, mark17_score, mark17_advice, mark17_details):
        export_data = {
            'date': datetime.datetime.now().strftime("%Y-%m-%d"),
            'update_time': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        raw_indicators = {}
        for d in [data_a, data_b, data_c]:
            if d: raw_indicators.update(d)
        if data_currency:
            for c in data_currency: raw_indicators[f"Currency_{c['name'].split(' ')[0]}"] = c['current']
        raw_indicators['Mark17_Score'] = mark17_score
        
        export_data['raw_indicators'] = raw_indicators
        export_data['us_jp_spread'] = {'us': data_d.get('US_10Y', 0), 'jp': data_d.get('JP_10Y', 0), 'spread': data_d.get('Spread', 0), 'status': "Danger" if data_d.get('Spread', 0) < 2.0 else "Safe"}
        export_data['metals'] = [{'name': m['name'], 'current': m['current'], 'drop': m['drop_pct'], 'status': "Danger" if m['drop_pct'] >= 50 else "Safe"} for m in data_e]
        export_data['currencies'] = data_currency
        export_data['global_markets'] = data_global
        export_data['total_score'] = mark17_score
        
        advice = "Safe"
        if mark17_score >= 15: advice = "Flee"
        elif mark17_score >= 12: advice = "Reduce"
        elif mark17_score >= 6: advice = "Caution"
        export_data['advice'] = advice
        
        def detail_status(detail_score):
            if detail_score == "-":
                return "Unavailable"
            match = re.search(r'[+]?(\d+(?:\.\d+)?)', str(detail_score))
            return "Warning" if match and float(match.group(1)) > 0 else "Safe"

        export_data['mark17_complete'] = not any(score == "-" for _, _, score in mark17_details)
        export_data['mark17'] = [
            {'item': item, 'value': value, 'score': item_score, 'status': detail_status(item_score)}
            for item, value, item_score in mark17_details
        ]

        return export_data


# ==========================================
# 主流程 (Headless Main)
# ==========================================
def upload_json(target_name, url, json_data, headers, timeout=60):
    """上傳同一份資料至單一網站，並回傳是否成功。"""
    log_msg(f"-> 正在上傳至 {target_name}...")
    try:
        response = requests.post(url, json=json_data, headers=headers, timeout=timeout)
        if 200 <= response.status_code < 300:
            log_msg(f"✅ {target_name} 上傳成功！")
            return True
        detail = response.text[:500].replace('\n', ' ')
        log_msg(f"⚠️ {target_name} 上傳失敗 (HTTP {response.status_code}): {detail}")
    except Exception as error:
        log_msg(f"❌ {target_name} 連線異常: {error}")
    return False


def main():
    print("==============================================")
    print("      MacroWave 自動抓取與同步腳本 (全自動版)      ")
    print("==============================================\n")
    if APP_CONFIG["fred_api_key"]:
        log_msg(f"✅ FRED API Key 已載入（來源：{APP_CONFIG['fred_api_key_source']}）")
    else:
        log_msg("⚠️ 尚未設定 FRED API Key；FRED 指標將使用備援值。")
        log_msg("請確認 JSON 內含 fred_api_key 或 FRED_API_KEY，並放在下列任一位置：")
        for config_path in APP_CONFIG["config_paths"]:
            log_msg(f"  - {config_path}")
    
    setup_driver()

    log_msg("=== 階段 1: 開始抓取數據 ===")
    
    log_msg("-> 1/6 總經指標 (A/B/C)")
    data_a = MacroWaveA_Logic().run()
    lbc = MacroWaveBC_Logic()
    data_b = lbc.run_b()
    data_c = lbc.run_c()

    log_msg("-> 2/6 美日利差")
    data_d = MacroWaveD_Logic().run()

    log_msg("-> 3/6 貴金屬")
    data_e = MacroWaveE_Logic().get_data()

    log_msg("-> 4/6 匯率")
    data_currency = MacroWaveCurrency_Logic().get_data()

    log_msg("-> 5/6 全球股市")
    data_global = MacroWaveGlobalMarket_Logic().get_data()

    log_msg("-> 6/6 計算 Mark 17 (包含 FRED 數據)")
    score, details = MacroWaveMark17_Logic().calculate_score(data_a, data_b, data_c)

    log_msg("=== 階段 2: 產生並儲存 JSON ===")
    json_data = MacroWaveJSON_Logic().generate_json(
        data_a, data_b, data_c, data_d, data_e,
        data_currency, data_global, score, "", details
    )

    if getattr(sys, 'frozen', False):
        base_dir = os.path.dirname(sys.executable)
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        
    time_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"macrowave_data_{time_str}.json"
    save_path = os.path.join(base_dir, filename)

    try:
        with open(save_path, 'w', encoding='utf-8') as outfile:
            json.dump(json_data, outfile, indent=4, ensure_ascii=False)
        log_msg(f"✅ 本地 JSON 儲存成功: {save_path}")
    except Exception as e:
        log_msg(f"❌ 儲存失敗: {e}")
        return

    log_msg("=== 階段 3: API 同步上傳 ===")
    api_key = APP_CONFIG["upload_api_key"]
    headers = {'X-Api-Key': api_key}

    upload_json(
        "原 MacroWave Vercel",
        "https://macrowave-nuxt.vercel.app/api/upload/",
        json_data,
        headers,
        timeout=30,
    )

    upload_json(
        "590bbs MacroWave 總經戰情室",
        "https://590bbs.vercel.app/api/macrowave/upload",
        json_data,
        headers,
        timeout=60,
    )

    log_msg("-> 傳送喚醒訊號給 Render 伺服器...")
    try: requests.get("https://macrowave-web.onrender.com/", timeout=5)
    except: pass

    log_msg("-> 等待 70 秒讓 Render 伺服器啟動...")
    for i in range(70, 0, -1):
        if i % 10 == 0 or i <= 5:
            print(f"   倒數 {i} 秒...")
        time.sleep(1)

    upload_json(
        "原 MacroWave Render",
        "https://macrowave-web.onrender.com/api/upload/",
        json_data,
        headers,
        timeout=60,
    )

    print("\n==============================================")
    log_msg("🎉 全部更新流程執行完畢！您可以安全關閉此視窗。")
    print("==============================================")
    if getattr(sys, 'frozen', False):
        input("按 Enter 關閉視窗...")

if __name__ == "__main__":
    main()
