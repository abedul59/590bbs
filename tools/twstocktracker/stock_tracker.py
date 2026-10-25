import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import requests
import json
from datetime import datetime
import glob
import re
import threading
import csv
import os
import sys
import time
import webbrowser
from bs4 import BeautifulSoup

# 導入繪圖套件
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# 設定 matplotlib 支援顯示繁體中文與正常顯示負號
plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei', 'PingFang HK', 'SimHei', 'Arial']
plt.rcParams['axes.unicode_minus'] = False

DASHBOARD_URL = "https://590bbs.vercel.app/macrowave?view=twstocktracker"
SYNC_TARGETS = [
    ("590bbs 隱藏後台", "https://590bbs.vercel.app/api/twstocktracker/sync"),
    ("原 TwStockTracker", "https://twstocktracker-web.vercel.app/api/sync"),
]
REQUEST_TIMEOUT = (10, 45)
DEFAULT_TOKEN = "macrowave168"


def configure_working_directory():
    """確保雙擊 EXE、排程器與 Python 執行都從程式所在目錄讀寫。"""
    program_path = sys.executable if getattr(sys, 'frozen', False) else __file__
    os.chdir(os.path.dirname(os.path.abspath(program_path)))


def normalize_change_percent(sign, percent):
    raw = str(percent).strip().replace('%', '')
    if raw in ('', '-', '--', '---'):
        return None
    try:
        value = abs(float(raw.replace(',', '')))
    except ValueError:
        return None
    if str(sign).strip() == '-':
        value = -value
    return f"{value:+.2f}%" if value else "0.00%"


def validate_export_payload(payload):
    if not isinstance(payload, dict) or not re.fullmatch(r'\d{14}', str(payload.get('date', ''))):
        raise ValueError("date 必須是 14 位時間戳記 YYYYMMDDhhmmss")
    stats = payload.get('yahoo_stats')
    top30 = payload.get('yahoo_top30')
    if not isinstance(stats, list) or not isinstance(top30, list):
        raise ValueError("yahoo_stats 與 yahoo_top30 必須是陣列")
    if not stats and not top30:
        raise ValueError("尚無類股統計或 Top 30 資料，請先抓取個股數據")
    return True


def upload_payload(payload, token=DEFAULT_TOKEN, targets=None, retries=3, session=requests):
    """同步新後台並保留舊站備援；單一站台失敗不阻擋其他站台。"""
    validate_export_payload(payload)
    results = {}
    headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {token}'}
    for name, url in targets or SYNC_TARGETS:
        last_error = "未知錯誤"
        for attempt in range(1, retries + 1):
            try:
                response = session.post(url, json=payload, headers=headers, timeout=REQUEST_TIMEOUT)
                response.raise_for_status()
                results[name] = {'success': True, 'url': url, 'message': '同步成功'}
                break
            except requests.RequestException as exc:
                last_error = str(exc)
                if attempt < retries:
                    time.sleep(2)
        else:
            results[name] = {'success': False, 'url': url, 'message': last_error}
    return results


def load_settings(path='stock_tracker_settings.json'):
    settings = {'api_token': DEFAULT_TOKEN, 'sync_original_site': True}
    if not os.path.exists(path):
        return settings
    try:
        with open(path, 'r', encoding='utf-8-sig') as handle:
            saved = json.load(handle)
        if isinstance(saved, dict):
            settings.update({key: saved[key] for key in settings if key in saved})
    except (OSError, json.JSONDecodeError) as exc:
        print(f"讀取 {path} 失敗，使用預設設定：{exc}")
    return settings

class StockClassTracker:
    def __init__(self, root):
        self.root = root
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/122 Safari/537.36'})
        self.settings = load_settings()
        self.root.title("台股全方位資金流向與個股追蹤系統 (590bbs 同步版)")
        self.root.geometry("1300x950") 
        
        # ================= 頂部全局控制區 =================
        global_frame = tk.Frame(root, pady=10, bg="#e3f2fd")
        global_frame.pack(fill=tk.X)
        
        # 標題
        lbl_title = tk.Label(global_frame, text="台股資金流向追蹤系統", font=("微軟正黑體", 14, "bold"), bg="#e3f2fd", fg="#0d47a1")
        lbl_title.pack(side=tk.LEFT, padx=15)
        
        # 總匯出與上傳按鈕 (移除輸入框，版面更乾淨)
        self.btn_master_export = tk.Button(global_frame, text="🌟 一鍵儲存 JSON 並推送到 Nuxt 網站", 
                                           command=self.export_and_upload_json, bg="#E91E63", fg="white", font=("微軟正黑體", 11, "bold"))
        self.btn_master_export.pack(side=tk.RIGHT, padx=20)

        self.btn_open_dashboard = tk.Button(global_frame, text="🌐 開啟目前網站", command=lambda: webbrowser.open(DASHBOARD_URL), bg="#1565C0", fg="white", font=("微軟正黑體", 10, "bold"))
        self.btn_open_dashboard.pack(side=tk.RIGHT, padx=5)
        
        # ================= 建立分頁系統 =================
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.tab_daily = tk.Frame(self.notebook)
        self.tab_accum = tk.Frame(self.notebook)
        self.tab_detail = tk.Frame(self.notebook)
        self.tab_chart = tk.Frame(self.notebook) 
        self.tab_stats = tk.Frame(self.notebook) 
        self.tab_top30 = tk.Frame(self.notebook)
        
        self.notebook.add(self.tab_daily, text="每日收盤數據 (類股)")
        self.notebook.add(self.tab_accum, text="波段累計合計 (週/月)")
        self.notebook.add(self.tab_detail, text="個股詳細數據 (三市場)")
        self.notebook.add(self.tab_chart, text="📊 各類股平均圖表")
        self.notebook.add(self.tab_stats, text="📈 類股數據總覽")
        self.notebook.add(self.tab_top30, text="🔥 每日成交金額 Top 30")
        
        self.setup_daily_tab()
        self.setup_accum_tab()
        self.setup_detail_tab()
        self.setup_chart_tab()
        self.setup_stats_tab()
        self.setup_top30_tab()
        
        self.canvas = None
        self.refresh_all_data()

    # ================= 分頁 1: 每日收盤數據 =================
    def setup_daily_tab(self):
        control_frame = tk.Frame(self.tab_daily, pady=10)
        control_frame.pack(fill=tk.X, padx=10)
        self.scrape_btn = tk.Button(control_frame, text="透過證交所抓取今日類股數據", command=self.scrape_and_save, bg="#4CAF50", fg="white")
        self.scrape_btn.pack(side=tk.LEFT, padx=5)
        tk.Label(control_frame, text="自動載入歷史紀錄:").pack(side=tk.LEFT, padx=5)
        self.file_var = tk.StringVar()
        self.json_dropdown = ttk.Combobox(control_frame, textvariable=self.file_var, state="readonly", width=25)
        self.json_dropdown.pack(side=tk.LEFT, padx=5)
        self.json_dropdown.bind("<<ComboboxSelected>>", self.load_selected_json)
        
        tree_frame = tk.Frame(self.tab_daily)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        columns = ("Category", "ClosePoint", "ChangePercent")
        self.tree_daily = ttk.Treeview(tree_frame, columns=columns, show="headings")
        self.tree_daily.heading("Category", text="類股名稱")
        self.tree_daily.heading("ClosePoint", text="收盤指數 (點)")
        self.tree_daily.heading("ChangePercent", text="單日漲跌幅 (%)")
        self.tree_daily.column("Category", anchor=tk.CENTER, width=180)
        self.tree_daily.column("ClosePoint", anchor=tk.CENTER, width=150)
        self.tree_daily.column("ChangePercent", anchor=tk.CENTER, width=150)
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree_daily.yview)
        self.tree_daily.configure(yscroll=scrollbar.set)
        self.tree_daily.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    # ================= 分頁 2: 波段累計合計 =================
    def setup_accum_tab(self):
        control_frame = tk.Frame(self.tab_accum, pady=10)
        control_frame.pack(fill=tk.X, padx=10)
        tk.Label(control_frame, text="選擇計算區間:").pack(side=tk.LEFT, padx=5)
        self.period_var = tk.StringVar()
        self.period_dropdown = ttk.Combobox(control_frame, textvariable=self.period_var, state="readonly", width=25)
        self.period_dropdown['values'] = ["全部累積", "近 5 個交易日", "近 10 個交易日", "近 20 個交易日"]
        self.period_dropdown.current(0)
        self.period_dropdown.pack(side=tk.LEFT, padx=5)
        self.period_dropdown.bind("<<ComboboxSelected>>", lambda e: self.calculate_accumulation())
        self.lbl_accum_info = tk.Label(control_frame, text="準備計算中...", fg="blue")
        self.lbl_accum_info.pack(side=tk.LEFT, padx=15)
        tk.Button(control_frame, text="重新計算合計", command=self.calculate_accumulation).pack(side=tk.RIGHT, padx=5)
        
        tree_frame = tk.Frame(self.tab_accum)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        columns = ("Category", "TotalChangePercent")
        self.tree_accum = ttk.Treeview(tree_frame, columns=columns, show="headings")
        self.tree_accum.heading("Category", text="類股名稱")
        self.tree_accum.heading("TotalChangePercent", text="波段累計漲跌幅 (%)")
        self.tree_accum.column("Category", anchor=tk.CENTER, width=200)
        self.tree_accum.column("TotalChangePercent", anchor=tk.CENTER, width=200)
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree_accum.yview)
        self.tree_accum.configure(yscroll=scrollbar.set)
        self.tree_accum.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    # ================= 分頁 3: 個股詳細數據 =================
    def setup_detail_tab(self):
        control_frame = tk.Frame(self.tab_detail, pady=10)
        control_frame.pack(fill=tk.X, padx=10)
        self.btn_scrape_detail = tk.Button(control_frame, text="抓取所有個股數據", command=self.start_scrape_detail_thread, bg="#2196F3", fg="white")
        self.btn_scrape_detail.pack(side=tk.LEFT, padx=5)
        
        self.btn_export_csv = tk.Button(control_frame, text="匯出明細 CSV", command=self.export_detail_to_csv, state=tk.DISABLED)
        self.btn_export_csv.pack(side=tk.LEFT, padx=5)
        
        self.lbl_detail_status = tk.Label(control_frame, text="點擊左側按鈕開始掃描 Yahoo 股市...", fg="#666")
        self.lbl_detail_status.pack(side=tk.LEFT, padx=15)
        self.progress = ttk.Progressbar(control_frame, orient=tk.HORIZONTAL, length=200, mode='determinate')
        self.progress.pack(side=tk.RIGHT, padx=10)
        
        tree_frame = tk.Frame(self.tab_detail)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        columns = ("Category", "Ticker", "Name", "Price", "Change", "ChangePct", "Open", "PrevClose", "High", "Low", "Volume")
        self.tree_detail = ttk.Treeview(tree_frame, columns=columns, show="headings")
        headings = ["類別", "代號", "名稱", "股價", "漲跌", "漲跌幅(%)", "開盤", "昨收", "最高", "最低", "成交量"]
        widths = [110, 80, 120, 70, 70, 80, 70, 70, 70, 70, 90]
        for col, head, width in zip(columns, headings, widths):
            self.tree_detail.heading(col, text=head)
            self.tree_detail.column(col, anchor=tk.CENTER, width=width)
            
        scrollbar_y = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree_detail.yview)
        scrollbar_x = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.tree_detail.xview)
        self.tree_detail.configure(yscroll=scrollbar_y.set, xscroll=scrollbar_x.set)
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.tree_detail.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)

    # ================= 分頁 4: 圖表顯示區 =================
    def setup_chart_tab(self):
        self.chart_frame = tk.Frame(self.tab_chart, bg="white")
        self.chart_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.lbl_chart_hint = tk.Label(self.chart_frame, text="請先至「個股詳細數據」分頁點擊抓取，圖表與數據總覽將自動生成。", font=("微軟正黑體", 14), bg="white", fg="#666")
        self.lbl_chart_hint.pack(expand=True)

    # ================= 分頁 5: 三層平均數據總覽 =================
    def setup_stats_tab(self):
        frame_tse = tk.LabelFrame(self.tab_stats, text="【 上市類股 】 平均數據排序", font=("微軟正黑體", 11, "bold"), fg="#D32F2F")
        frame_tse.pack(fill=tk.BOTH, expand=True, padx=10, pady=2)
        frame_otc = tk.LabelFrame(self.tab_stats, text="【 上櫃類股 】 平均數據排序", font=("微軟正黑體", 11, "bold"), fg="#1976D2")
        frame_otc.pack(fill=tk.BOTH, expand=True, padx=10, pady=2)
        frame_emg = tk.LabelFrame(self.tab_stats, text="【 興櫃類股 】 平均數據排序", font=("微軟正黑體", 11, "bold"), fg="#388E3C")
        frame_emg.pack(fill=tk.BOTH, expand=True, padx=10, pady=2)
        
        columns = ("Category", "AvgChangePct", "AvgPrice", "AvgVol")
        headings = ["類股名稱", "平均漲跌幅 (%)", "平均股價 (元)", "平均成交量 (張)"]
        
        self.tree_tse_stats = self._create_stats_treeview(frame_tse, columns, headings)
        self.tree_otc_stats = self._create_stats_treeview(frame_otc, columns, headings)
        self.tree_emg_stats = self._create_stats_treeview(frame_emg, columns, headings)

    def _create_stats_treeview(self, parent_frame, columns, headings):
        tree = ttk.Treeview(parent_frame, columns=columns, show="headings", height=5)
        for col, head in zip(columns, headings):
            tree.heading(col, text=head)
            tree.column(col, anchor=tk.CENTER)
        scroll = ttk.Scrollbar(parent_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscroll=scroll.set)
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        return tree

    # ================= 分頁 6: 成交額 Top 30 =================
    def setup_top30_tab(self):
        control_frame = tk.Frame(self.tab_top30, pady=10)
        control_frame.pack(fill=tk.X, padx=10)
        self.btn_export_top30 = tk.Button(control_frame, text="匯出 Top 30 代碼 CSV (供看盤軟體)", command=self.export_top30_csv, bg="#9C27B0", fg="white", state=tk.DISABLED)
        self.btn_export_top30.pack(side=tk.LEFT, padx=5)
        
        tree_frame = tk.Frame(self.tab_top30)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        columns = ("Rank", "Ticker", "Name", "Market", "TotalValue")
        self.tree_top30 = ttk.Treeview(tree_frame, columns=columns, show="headings")
        headings = ["排名", "股票代碼", "股票名稱", "所屬市場", "估算成交金額 (千元)"]
        widths = [50, 100, 150, 100, 200]
        for col, head, width in zip(columns, headings, widths):
            self.tree_top30.heading(col, text=head)
            self.tree_top30.column(col, anchor=tk.CENTER, width=width)
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree_top30.yview)
        self.tree_top30.configure(yscroll=scrollbar.set)
        self.tree_top30.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def _update_status(self, text):
        self.root.after(0, lambda: self.lbl_detail_status.config(text=text))

    def _update_progress(self, current, maximum):
        self.root.after(0, lambda: self.progress.config(value=current, maximum=maximum))

    # ================= 大盤資料邏輯 =================
    def scrape_and_save(self):
        url = "https://www.twse.com.tw/rwd/zh/afterTrading/MI_INDEX?response=json&type=IND"
        try:
            self.scrape_btn.config(text="抓取中...", state=tk.DISABLED)
            self.root.update()
            response = self.session.get(url, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            json_data = response.json()
            data_list = []
            if 'tables' in json_data:
                for table in json_data['tables']:
                    fields = table.get('fields', [])
                    if '指數' in fields and '漲跌百分比(%)' in fields:
                        name_idx, close_idx, percent_idx = fields.index('指數'), fields.index('收盤指數'), fields.index('漲跌百分比(%)')
                        sign_idx = fields.index('漲跌(+/-)') if '漲跌(+/-)' in fields else -1
                        for row in table.get('data', []):
                            name = str(row[name_idx]).strip()
                            close_point = str(row[close_idx]).strip().replace(',', '')
                            sign = ""
                            if sign_idx != -1:
                                raw_sign = re.sub(r'<[^>]+>', '', str(row[sign_idx])).strip()
                                if raw_sign in ['+', '-']: sign = raw_sign
                            change_percent = normalize_change_percent(sign, row[percent_idx])
                            if change_percent is None:
                                continue
                            data_list.append({"category": name, "close_point": close_point, "change_percent": change_percent})
                        break 
            if not data_list:
                raise ValueError("證交所回應中找不到類股指數資料，可能是休市或欄位格式已變更")
            date_str = datetime.now().strftime("%Y%m%d")
            with open(f"twse_class_{date_str}.json", 'w', encoding='utf-8') as f:
                json.dump(data_list, f, ensure_ascii=False, indent=4)
            messagebox.showinfo("成功", "今日大盤數據已成功抓取並儲存。")
            self.refresh_all_data()
        except Exception as e:
            messagebox.showerror("錯誤", str(e))
        finally:
            self.scrape_btn.config(text="透過證交所抓取今日類股數據", state=tk.NORMAL)

    def refresh_all_data(self):
        json_files = sorted(glob.glob("twse_class_*.json"), reverse=True)
        self.json_dropdown['values'] = json_files
        if json_files:
            self.json_dropdown.current(0)
            self.load_selected_json()
        self.calculate_accumulation()

    def load_selected_json(self, event=None):
        selected_file = self.file_var.get()
        if not selected_file: return
        try:
            with open(selected_file, 'r', encoding='utf-8') as f: data_list = json.load(f)
            self.tree_daily.delete(*self.tree_daily.get_children())
            for item in data_list:
                self.tree_daily.insert("", tk.END, values=(item.get("category", ""), item.get("close_point", ""), item.get("change_percent", "")))
        except: pass

    def calculate_accumulation(self):
        json_files = sorted(glob.glob("twse_class_*.json"), reverse=True)
        self.tree_accum.delete(*self.tree_accum.get_children())
        if not json_files: return
        period_str = self.period_var.get()
        target_days = 5 if "5" in period_str else 10 if "10" in period_str else 20 if "20" in period_str else len(json_files)
        category_totals = {}
        for file in json_files[:target_days]:
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    for item in json.load(f):
                        cat = item.get("category", "")
                        match = re.search(r'(-?[\d\.]+)', item.get("change_percent", "0"))
                        val = float(match.group(1)) if match else 0.0
                        if cat not in category_totals: category_totals[cat] = 0.0
                        category_totals[cat] += val
            except: pass 
        for cat, total in sorted(category_totals.items(), key=lambda x: x[1], reverse=True):
            self.tree_accum.insert("", tk.END, values=(cat, f"{'+' if total > 0 else ''}{total:.2f}%"))
        self.lbl_accum_info.config(text=f"顯示區間：實際合計了 {len(json_files[:target_days])} 個交易日")

    def start_scrape_detail_thread(self):
        self.btn_scrape_detail.config(state=tk.DISABLED, text="全自動掃描中...")
        self.btn_export_csv.config(state=tk.DISABLED)
        self.btn_export_top30.config(state=tk.DISABLED)
        self.tree_detail.delete(*self.tree_detail.get_children())
        self.tree_top30.delete(*self.tree_top30.get_children())
        if hasattr(self, 'lbl_chart_hint') and self.lbl_chart_hint.winfo_exists():
            self.lbl_chart_hint.destroy()
        threading.Thread(target=self._scrape_yahoo_details, daemon=True).start()

    def _scrape_yahoo_details(self):
        scrape_succeeded = False
        try:
            self._update_status("正在獲取所有類股分類清單...")
            res = self.session.get("https://tw.stock.yahoo.com/class", timeout=REQUEST_TIMEOUT)
            res.raise_for_status()
            soup = BeautifulSoup(res.text, 'html.parser')
            
            links = []
            seen_urls = set()
            for a in soup.find_all('a', href=re.compile(r'/class-quote\?sectorId=')):
                url = "https://tw.stock.yahoo.com" + a['href'] if not a['href'].startswith('http') else a['href']
                cat_name = a.text.strip()
                if cat_name and url not in seen_urls:
                    if cat_name.startswith("興"): prefix = "興櫃-"
                    elif "TWO" in url: prefix = "上櫃-"
                    else: prefix = "上市-"
                    links.append((prefix + cat_name, url))
                    seen_urls.add(url)

            if not links:
                raise ValueError("Yahoo 類股頁找不到任何分類連結，網站版型可能已更新")

            total_cats = len(links)
            self._update_progress(0, total_cats)
            total_stocks = 0
            category_stats = {} 
            top30_candidates = []
            
            for i, (cat_name, url) in enumerate(links):
                self._update_status(f"正在掃描 ({i+1}/{total_cats}): {cat_name} ...")
                if cat_name not in category_stats:
                    category_stats[cat_name] = {"pct_sum": 0.0, "pct_count": 0, "price_sum": 0.0, "price_count": 0, "vol_sum": 0.0, "vol_count": 0}
                    
                seen_tickers = set() 
                try:
                    cat_res = self.session.get(url, timeout=REQUEST_TIMEOUT)
                    cat_res.raise_for_status()
                    cat_soup = BeautifulSoup(cat_res.text, 'html.parser')
                    rows = cat_soup.find_all('div', class_=lambda x: x and 'table-row' in x)
                    
                    for row in rows:
                        cols = row.find_all('div', recursive=False)
                        data = []
                        for col in cols:
                            texts = list(col.stripped_strings)
                            if not texts: continue
                            is_negative = bool(col.find(class_=lambda c: c and ('trend-down' in c or 'C(#009900)' in c)))
                            if is_negative:
                                for j in range(len(texts)):
                                    if re.match(r'^[\d\.]+%?$', texts[j]): texts[j] = "-" + texts[j]
                            data.extend(texts)
                            
                        ticker_idx = -1
                        for j, val in enumerate(data):
                            if re.match(r'^[A-Za-z0-9]+\.(TW|TWO|TE)$', val):
                                ticker_idx = j
                                break
                                
                        if ticker_idx != -1:
                            ticker = data[ticker_idx].replace('.TW', '').replace('.TWO', '').replace('.TE', '')
                            if not ticker or ticker in seen_tickers: continue
                            
                            def get_val(offset):
                                idx = ticker_idx + offset
                                return data[idx] if idx < len(data) else "-"
                                
                            name = data[ticker_idx - 1] if ticker_idx > 0 else "N/A"
                            price, change, change_pct = get_val(1), get_val(2), get_val(3)
                            open_p, prev_c, high, low, vol = get_val(4), get_val(5), get_val(6), get_val(7), get_val(8)
                            
                            if price == "-" or "---" in price or change_pct == "-": continue
                                
                            seen_tickers.add(ticker)
                            row_values = (cat_name, ticker, name, price, change, change_pct, open_p, prev_c, high, low, vol)
                            self.root.after(0, lambda v=row_values: self.tree_detail.insert("", tk.END, values=v))
                            total_stocks += 1
                            
                            # 估算平均成交金額
                            try:
                                h_val = float(high.replace(',', ''))
                                l_val = float(low.replace(',', ''))
                                avg_p = (h_val + l_val) / 2.0
                            except:
                                try: avg_p = float(price.replace(',', ''))
                                except: avg_p = 0.0
                                
                            try: v_val = float(vol.replace(',', ''))
                            except: v_val = 0.0
                            
                            total_val = avg_p * v_val
                            if total_val > 0:
                                top30_candidates.append({
                                    "ticker": ticker, "name": name,
                                    "market": cat_name.split('-')[0], "total_val": total_val
                                })
                            
                            # 統計數據
                            match_pct = re.search(r'(-?[\d\.]+)', change_pct)
                            if match_pct:
                                try:
                                    category_stats[cat_name]["pct_sum"] += float(match_pct.group(1))
                                    category_stats[cat_name]["pct_count"] += 1
                                except ValueError: pass
                                
                            price_cln = price.replace(',', '').strip()
                            if price_cln.replace('.', '', 1).isdigit():
                                category_stats[cat_name]["price_sum"] += float(price_cln)
                                category_stats[cat_name]["price_count"] += 1
                                
                            vol_cln = vol.replace(',', '').strip()
                            if vol_cln.isdigit():
                                category_stats[cat_name]["vol_sum"] += float(vol_cln)
                                category_stats[cat_name]["vol_count"] += 1

                except Exception as e: print(f"掃描 {cat_name} 發生錯誤: {e}")
                self._update_progress(i + 1, total_cats)

            self._update_status(f"掃描完成！共抓取 {total_stocks} 檔有效個股資料。正在生成報表...")
            if total_stocks == 0:
                raise ValueError("Yahoo 分類頁沒有解析到任何個股，網站版型可能已更新")
            
            top30_candidates.sort(key=lambda x: x["total_val"], reverse=True)
            top30_results = top30_candidates[:30]
            
            self.root.after(0, lambda: self.update_top30_view(top30_results))
            self.root.after(0, lambda: self.draw_category_chart(category_stats))
            self.root.after(0, lambda: self.update_stats_view(category_stats))
            scrape_succeeded = True
            
        except Exception as e: self._update_status(f"系統發生錯誤: {e}")
        finally:
            self.root.after(0, lambda: self.btn_scrape_detail.config(state=tk.NORMAL, text="重新抓取個股數據"))
            if scrape_succeeded:
                self.root.after(0, lambda: self.btn_export_csv.config(state=tk.NORMAL))

    def update_top30_view(self, top30_results):
        self.tree_top30.delete(*self.tree_top30.get_children())
        for idx, item in enumerate(top30_results, 1):
            val_str = f"{int(item['total_val']):,}"
            self.tree_top30.insert("", tk.END, values=(idx, item['ticker'], item['name'], item['market'], val_str))
        if top30_results: self.btn_export_top30.config(state=tk.NORMAL)

    def draw_category_chart(self, category_stats):
        tse_stats, otc_stats, emg_stats = [], [], []
        for cat, data in category_stats.items():
            if data["pct_count"] > 0:
                avg = data["pct_sum"] / data["pct_count"]
                if cat.startswith("上市-"): tse_stats.append((cat.replace("上市-", ""), avg))
                elif cat.startswith("上櫃-"): otc_stats.append((cat.replace("上櫃-", ""), avg))
                elif cat.startswith("興櫃-"): emg_stats.append((cat.replace("興櫃-", ""), avg))
                    
        tse_stats.sort(key=lambda x: x[1], reverse=True)
        otc_stats.sort(key=lambda x: x[1], reverse=True)
        emg_stats.sort(key=lambda x: x[1], reverse=True)
            
        if self.canvas: self.canvas.get_tk_widget().destroy()
        fig, axes = plt.subplots(3, 1, figsize=(12, 14))
        
        def _plot_ax(ax, stats, title):
            if not stats: return
            categories = [x[0] for x in stats]
            averages = [x[1] for x in stats]
            colors = ['#FF3333' if val > 0 else '#009900' for val in averages]
            bars = ax.bar(categories, averages, color=colors)
            ax.set_title(title, fontsize=14, fontweight='bold')
            ax.set_ylabel("平均漲跌幅 (%)", fontsize=9)
            ax.axhline(0, color='black', linewidth=1)
            ax.set_xticks(range(len(categories)))
            ax.set_xticklabels(categories, rotation=45, ha='right', fontsize=8)
            for bar in bars:
                yval = bar.get_height()
                offset = 0.1 if yval >= 0 else -0.4
                ax.text(bar.get_x() + bar.get_width()/2.0, yval + offset, f"{yval:.2f}%", ha='center', va='bottom' if yval >= 0 else 'top', fontsize=8)

        _plot_ax(axes[0], tse_stats, "上市類股平均漲跌幅")
        _plot_ax(axes[1], otc_stats, "上櫃類股平均漲跌幅")
        _plot_ax(axes[2], emg_stats, "興櫃類股平均漲跌幅")

        fig.tight_layout(pad=2.0)
        self.canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def update_stats_view(self, category_stats):
        self.tree_tse_stats.delete(*self.tree_tse_stats.get_children())
        self.tree_otc_stats.delete(*self.tree_otc_stats.get_children())
        self.tree_emg_stats.delete(*self.tree_emg_stats.get_children())
        
        tse_list, otc_list, emg_list = [], [], []
        for cat, data in category_stats.items():
            avg_pct = data["pct_sum"] / data["pct_count"] if data["pct_count"] > 0 else 0
            avg_price = data["price_sum"] / data["price_count"] if data["price_count"] > 0 else 0
            avg_vol = data["vol_sum"] / data["vol_count"] if data["vol_count"] > 0 else 0
            
            sign = "+" if avg_pct > 0 else ""
            display_name = cat.replace("上市-", "").replace("上櫃-", "").replace("興櫃-", "")
            
            row_data = (avg_pct, (display_name, f"{sign}{avg_pct:.2f}%", f"{avg_price:.2f}", f"{int(avg_vol):,}"))
            if cat.startswith("上市-"): tse_list.append(row_data)
            elif cat.startswith("上櫃-"): otc_list.append(row_data)
            elif cat.startswith("興櫃-"): emg_list.append(row_data)
                
        tse_list.sort(key=lambda x: x[0], reverse=True)
        otc_list.sort(key=lambda x: x[0], reverse=True)
        emg_list.sort(key=lambda x: x[0], reverse=True)
        
        for item in tse_list: self.tree_tse_stats.insert("", tk.END, values=item[1])
        for item in otc_list: self.tree_otc_stats.insert("", tk.END, values=item[1])
        for item in emg_list: self.tree_emg_stats.insert("", tk.END, values=item[1])

    def export_top30_csv(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="匯出 Top 30 股票代碼",
            initialfile=f"top30_tickers_{datetime.now().strftime('%Y%m%d')}.csv"
        )
        if not file_path: return
        try:
            with open(file_path, mode='w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                for child in self.tree_top30.get_children():
                    ticker = self.tree_top30.item(child)["values"][1]
                    writer.writerow([ticker])
            messagebox.showinfo("成功", "Top 30 代碼已成功匯出。")
        except Exception as e:
            messagebox.showerror("錯誤", str(e))

    def export_detail_to_csv(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="匯出個股資料 CSV",
            initialfile=f"yahoo_stocks_{datetime.now().strftime('%Y%m%d')}.csv"
        )
        if not file_path: return
        try:
            with open(file_path, mode='w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                writer.writerow(["類別", "代號", "名稱", "股價", "漲跌", "漲跌幅(%)", "開盤", "昨收", "最高", "最低", "成交量"])
                for child in self.tree_detail.get_children():
                    writer.writerow(self.tree_detail.item(child)["values"])
            messagebox.showinfo("成功", "資料已成功匯出至 CSV。")
        except Exception as e:
            messagebox.showerror("錯誤", str(e))

    # ================= 本地儲存並同步到目前網站 =================
    def export_and_upload_json(self):
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="儲存全數據 JSON",
            initialfile=f"stock_master_data_{timestamp}.json"
        )
        if not file_path: return
        
        try:
            # 1. 收集所有資料
            daily_data = [{"category": self.tree_daily.item(c)["values"][0], "close_point": self.tree_daily.item(c)["values"][1], "change_percent": self.tree_daily.item(c)["values"][2]} for c in self.tree_daily.get_children()]
            accum_data = [{"category": self.tree_accum.item(c)["values"][0], "total_change_percent": self.tree_accum.item(c)["values"][1]} for c in self.tree_accum.get_children()]
            
            details = []
            for c in self.tree_detail.get_children():
                v = self.tree_detail.item(c)["values"]
                details.append({"category": v[0], "ticker": str(v[1]), "name": v[2], "price": v[3], "change": v[4], "change_pct": v[5], "open": v[6], "prev_close": v[7], "high": v[8], "low": v[9], "volume": v[10]})
                
            stats = []
            for tree, market in [(self.tree_tse_stats, "上市"), (self.tree_otc_stats, "上櫃"), (self.tree_emg_stats, "興櫃")]:
                for c in tree.get_children():
                    v = tree.item(c)["values"]
                    stats.append({"market": market, "category": v[0], "avg_change_pct": v[1], "avg_price": v[2], "avg_vol": v[3]})
                    
            top30_data = []
            for c in self.tree_top30.get_children():
                v = self.tree_top30.item(c)["values"]
                top30_data.append({"rank": v[0], "ticker": str(v[1]), "name": v[2], "market": v[3], "total_value": v[4]})
                
            export_data = {
                "date": timestamp,
                "twse_daily": daily_data, "twse_accum": accum_data,
                "yahoo_details": details, "yahoo_stats": stats, "yahoo_top30": top30_data,
                "dashboard_url": DASHBOARD_URL,
                "generated_at": datetime.now().astimezone().isoformat(timespec='seconds')
            }
            validate_export_payload(export_data)
            
            # 2. 本地寫入
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=4)
                
            # 3. 背景同步；目前 590bbs 為主站，原站可在設定檔關閉。
            self.btn_master_export.config(state=tk.DISABLED, text="同步中...")
            targets = SYNC_TARGETS if self.settings.get('sync_original_site', True) else SYNC_TARGETS[:1]

            def send_request():
                results = upload_payload(
                    export_data,
                    token=str(self.settings.get('api_token') or DEFAULT_TOKEN),
                    targets=targets,
                    session=self.session,
                )
                successes = [name for name, result in results.items() if result['success']]
                failures = [f"{name}: {result['message']}" for name, result in results.items() if not result['success']]
                lines = [f"✅ 本地儲存完成：{file_path}"]
                if successes: lines.append(f"✅ 同步成功：{'、'.join(successes)}")
                if failures: lines.append("❌ 同步失敗：\n" + "\n".join(failures))

                def finish_upload():
                    self.btn_master_export.config(state=tk.NORMAL, text="🌟 一鍵儲存 JSON 並推送到 Nuxt 網站")
                    if failures:
                        messagebox.showwarning("同步結果", "\n".join(lines))
                    else:
                        messagebox.showinfo("同步結果", "\n".join(lines) + f"\n\n網站：{DASHBOARD_URL}")

                self.root.after(0, finish_upload)

            threading.Thread(target=send_request, daemon=True).start()
                
        except Exception as e:
            messagebox.showerror("發生錯誤", str(e))

if __name__ == "__main__":
    configure_working_directory()
    root = tk.Tk()
    app = StockClassTracker(root)
    root.mainloop()
