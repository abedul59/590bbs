import argparse
import importlib.util
import json
import os
import queue
import random
import subprocess
import sys
import threading
import time
import traceback
import webbrowser
from datetime import datetime
from pathlib import Path
import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk


APP_NAME = "MacroWave 全方位更新中心"
DASHBOARD_URL = "https://590bbs.vercel.app/macrowave"
CONFIG_NAME = "macrowave_all_in_one.json"
WORKERS = {
    "macrowave": {"title": "MacroWave／Mark 17", "description": "總經、領先指標、Mark 17 與市場資料"},
    "per_auto": {"title": "六大指標與本益比", "description": "股票六大指標、EPS 與目標價格區間"},
    "twstocktracker": {"title": "台股資金流向", "description": "類股漲跌、三市場個股與成交額 Top 30"},
    "bengo": {"title": "Bengo 大戶籌碼", "description": "大戶持股比例、人數與股價歷史"},
}
DEFAULT_CONFIG = {
    "fred_api_key": "",
    "upload_api_key": "macrowave168",
    "stock_ids": ["2330", "2317", "2603"],
    "target_month": datetime.now().month,
    "minimum_wait_seconds": 10,
    "maximum_wait_seconds": 30,
    "sync_legacy_sites": False,
    "selected_workers": list(WORKERS),
}


def app_directory():
    program = Path(sys.executable if getattr(sys, "frozen", False) else __file__).resolve()
    return program.parent


def resource_path(filename):
    if getattr(sys, "frozen", False):
        return Path(getattr(sys, "_MEIPASS")) / "workers" / filename
    root = Path(__file__).resolve().parents[1]
    paths = {
        "MacroWave_AutoSync.py": root / "macrowave_autosync" / "MacroWave_AutoSync.py",
        "PER_auto.py": root / "per_auto" / "PER_auto.py",
        "stock_tracker.py": root / "twstocktracker" / "stock_tracker.py",
        "bengo_auto.py": root / "bengo-auto" / "bengo_auto.py",
    }
    return paths[filename]


def normalize_stock_ids(value):
    if isinstance(value, str):
        values = value.replace(",", "\n").splitlines()
    elif isinstance(value, list):
        values = value
    else:
        values = []
    result = []
    for raw in values:
        stock_id = str(raw).strip().upper()
        if stock_id and stock_id.replace("-", "").isalnum() and 2 <= len(stock_id) <= 12:
            if stock_id not in result:
                result.append(stock_id)
    return result


def normalize_config(value):
    source = value if isinstance(value, dict) else {}
    config = dict(DEFAULT_CONFIG)
    config.update({key: source[key] for key in DEFAULT_CONFIG if key in source})
    config["fred_api_key"] = str(config["fred_api_key"] or "").strip()
    config["upload_api_key"] = str(config["upload_api_key"] or "macrowave168").strip()
    config["stock_ids"] = normalize_stock_ids(config["stock_ids"]) or list(DEFAULT_CONFIG["stock_ids"])
    config["target_month"] = min(12, max(1, int(config["target_month"])))
    config["minimum_wait_seconds"] = max(0, int(config["minimum_wait_seconds"]))
    config["maximum_wait_seconds"] = max(config["minimum_wait_seconds"], int(config["maximum_wait_seconds"]))
    config["sync_legacy_sites"] = bool(config["sync_legacy_sites"])
    config["selected_workers"] = [name for name in config["selected_workers"] if name in WORKERS] or list(WORKERS)
    return config


def load_config(directory=None):
    path = Path(directory or app_directory()) / CONFIG_NAME
    if not path.exists():
        return normalize_config({})
    try:
        return normalize_config(json.loads(path.read_text(encoding="utf-8-sig")))
    except (OSError, json.JSONDecodeError, TypeError, ValueError):
        return normalize_config({})


def save_config(config, directory=None):
    directory = Path(directory or app_directory())
    directory.mkdir(parents=True, exist_ok=True)
    config = normalize_config(config)
    (directory / CONFIG_NAME).write_text(json.dumps(config, ensure_ascii=False, indent=2), encoding="utf-8")
    (directory / "macrowave_config.json").write_text(json.dumps({
        "fred_api_key": config["fred_api_key"],
        "upload_api_key": config["upload_api_key"],
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    (directory / "stock_id_settings.csv").write_text("\n".join(config["stock_ids"]) + "\n", encoding="utf-8")
    (directory / "bengo_settings.json").write_text(json.dumps({
        "headless": True,
        "minimum_wait_seconds": config["minimum_wait_seconds"],
        "maximum_wait_seconds": config["maximum_wait_seconds"],
        "open_dashboard_when_finished": False,
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    (directory / "stock_tracker_settings.json").write_text(json.dumps({
        "api_token": config["upload_api_key"],
        "sync_original_site": config["sync_legacy_sites"],
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    return config


def load_worker_module(filename, module_name):
    path = resource_path(filename)
    if not path.exists():
        raise FileNotFoundError(f"找不到內建工作模組：{path}")
    spec = importlib.util.spec_from_file_location(module_name, path)
    if not spec or not spec.loader:
        raise ImportError(f"無法載入 {filename}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_macrowave_worker(config):
    module = load_worker_module("MacroWave_AutoSync.py", "embedded_macrowave")
    if module.APP_CONFIG["fred_api_key"]:
        module.log_msg(f"✅ FRED API Key 已載入（來源：{module.APP_CONFIG['fred_api_key_source']}）")
    else:
        module.log_msg("⚠️ 尚未設定 FRED API Key；FRED 指標將使用備援值。")

    module.setup_driver()
    module.log_msg("=== 階段 1: 開始抓取數據 ===")
    module.log_msg("-> 1/6 總經指標 (A/B/C)")
    data_a = module.MacroWaveA_Logic().run()
    logic_bc = module.MacroWaveBC_Logic()
    data_b = logic_bc.run_b()
    data_c = logic_bc.run_c()
    module.log_msg("-> 2/6 美日利差")
    data_d = module.MacroWaveD_Logic().run()
    module.log_msg("-> 3/6 貴金屬")
    data_e = module.MacroWaveE_Logic().get_data()
    module.log_msg("-> 4/6 匯率")
    data_currency = module.MacroWaveCurrency_Logic().get_data()
    module.log_msg("-> 5/6 全球股市")
    data_global = module.MacroWaveGlobalMarket_Logic().get_data()
    module.log_msg("-> 6/6 計算 Mark 17（包含 FRED 數據）")
    score, details = module.MacroWaveMark17_Logic().calculate_score(data_a, data_b, data_c)
    payload = module.MacroWaveJSON_Logic().generate_json(
        data_a, data_b, data_c, data_d, data_e,
        data_currency, data_global, score, "", details,
    )
    filename = f"macrowave_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    output_path = app_directory() / filename
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=4), encoding="utf-8")
    module.log_msg(f"✅ 本地 JSON 儲存成功: {output_path}")
    success = module.upload_json(
        "590bbs MacroWave 總經戰情室",
        "https://590bbs.vercel.app/api/macrowave/upload",
        payload,
        {"X-Api-Key": config["upload_api_key"]},
        timeout=60,
    )
    if not success:
        raise RuntimeError("MacroWave 資料已儲存，但同步 590bbs 失敗")


def run_per_worker(config):
    module = load_worker_module("PER_auto.py", "embedded_per_auto")
    if not config["sync_legacy_sites"]:
        module.UPLOAD_TARGETS = [target for target in module.UPLOAD_TARGETS if "590bbs.vercel.app" in target[1]]
    stock_ids = config["stock_ids"]
    for index, stock_id in enumerate(stock_ids, 1):
        print(f"\n[六大指標 {index}/{len(stock_ids)}] {stock_id}", flush=True)
        module.process_stock(stock_id, config["target_month"])
        if index < len(stock_ids):
            delay = random.randint(config["minimum_wait_seconds"], config["maximum_wait_seconds"])
            print(f"等待 {delay} 秒後處理下一檔…", flush=True)
            time.sleep(delay)


def run_bengo_worker(config):
    module = load_worker_module("bengo_auto.py", "embedded_bengo")
    result = module.main()
    if result not in (None, 0):
        raise RuntimeError(f"Bengo 工作結束碼：{result}")


def _tree_rows(tree, keys):
    result = []
    for child in tree.get_children():
        values = tree.item(child)["values"]
        result.append({key: values[index] if index < len(values) else "" for index, key in enumerate(keys)})
    return result


def run_twstocktracker_worker(config):
    module = load_worker_module("stock_tracker.py", "embedded_twstocktracker")
    root = tk.Tk()
    root.withdraw()
    notices = []
    original_messages = (module.messagebox.showinfo, module.messagebox.showwarning, module.messagebox.showerror)
    module.messagebox.showinfo = lambda title, text: notices.append(f"{title}: {text}")
    module.messagebox.showwarning = lambda title, text: notices.append(f"{title}: {text}")
    module.messagebox.showerror = lambda title, text: notices.append(f"{title}: {text}")
    try:
        app = module.StockClassTracker(root)
        print("抓取證交所類股資料…", flush=True)
        app.scrape_and_save()
        print("抓取 Yahoo 三市場個股資料…", flush=True)
        app._scrape_yahoo_details()
        for _ in range(3):
            root.update()

        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        stats = []
        for tree, market in ((app.tree_tse_stats, "上市"), (app.tree_otc_stats, "上櫃"), (app.tree_emg_stats, "興櫃")):
            for row in _tree_rows(tree, ("category", "avg_change_pct", "avg_price", "avg_vol")):
                row["market"] = market
                stats.append(row)
        payload = {
            "date": timestamp,
            "twse_daily": _tree_rows(app.tree_daily, ("category", "close_point", "change_percent")),
            "twse_accum": _tree_rows(app.tree_accum, ("category", "total_change_percent")),
            "yahoo_details": _tree_rows(app.tree_detail, ("category", "ticker", "name", "price", "change", "change_pct", "open", "prev_close", "high", "low", "volume")),
            "yahoo_stats": stats,
            "yahoo_top30": _tree_rows(app.tree_top30, ("rank", "ticker", "name", "market", "total_value")),
            "dashboard_url": module.DASHBOARD_URL,
            "generated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        }
        module.validate_export_payload(payload)
        backup = app_directory() / f"stock_master_data_{timestamp}.json"
        backup.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        targets = module.SYNC_TARGETS if config["sync_legacy_sites"] else module.SYNC_TARGETS[:1]
        results = module.upload_payload(payload, token=config["upload_api_key"], targets=targets, session=app.session)
        failed = [f"{name}: {item['message']}" for name, item in results.items() if not item["success"]]
        for notice in notices:
            print(notice, flush=True)
        if failed:
            raise RuntimeError("；".join(failed))
        print(f"台股資金流向同步完成：{backup}", flush=True)
    finally:
        module.messagebox.showinfo, module.messagebox.showwarning, module.messagebox.showerror = original_messages
        root.destroy()


def redirect_worker_output(log_file):
    if not log_file:
        return None
    path = Path(log_file)
    path.parent.mkdir(parents=True, exist_ok=True)
    handle = open(path, "a", encoding="utf-8", buffering=1)
    sys.stdout = handle
    sys.stderr = handle
    return handle


def run_worker(name, config_path=None):
    directory = Path(config_path).resolve().parent if config_path else app_directory()
    os.chdir(directory)
    config = load_config(directory)
    if config["fred_api_key"]:
        os.environ["FRED_API_KEY"] = config["fred_api_key"]
    os.environ["MACROWAVE_API_KEY"] = config["upload_api_key"]
    runners = {
        "macrowave": run_macrowave_worker,
        "per_auto": run_per_worker,
        "twstocktracker": run_twstocktracker_worker,
        "bengo": run_bengo_worker,
    }
    print(f"[{datetime.now().isoformat(timespec='seconds')}] 開始：{WORKERS[name]['title']}", flush=True)
    runners[name](config)
    print(f"[{datetime.now().isoformat(timespec='seconds')}] 完成：{WORKERS[name]['title']}", flush=True)


def worker_command(name, config_path, log_file):
    if getattr(sys, "frozen", False):
        return [sys.executable, "--worker", name, "--config", str(config_path), "--log-file", str(log_file)]
    return [sys.executable, str(Path(__file__).resolve()), "--worker", name, "--config", str(config_path), "--log-file", str(log_file)]


class AllInOneApp:
    def __init__(self, root):
        self.root = root
        self.root.title(APP_NAME)
        self.root.geometry("1040x760")
        self.root.minsize(820, 650)
        self.config = load_config()
        self.events = queue.Queue()
        self.running = False
        self.current_process = None
        self.worker_vars = {name: tk.BooleanVar(value=name in self.config["selected_workers"]) for name in WORKERS}
        self.status_vars = {name: tk.StringVar(value="等待中") for name in WORKERS}
        self.fred_var = tk.StringVar(value=self.config["fred_api_key"])
        self.upload_var = tk.StringVar(value=self.config["upload_api_key"])
        self.month_var = tk.IntVar(value=self.config["target_month"])
        self.min_wait_var = tk.IntVar(value=self.config["minimum_wait_seconds"])
        self.max_wait_var = tk.IntVar(value=self.config["maximum_wait_seconds"])
        self.legacy_var = tk.BooleanVar(value=self.config["sync_legacy_sites"])
        self._build_ui()
        self.root.after(150, self._drain_events)

    def _build_ui(self):
        header = tk.Frame(self.root, bg="#0f172a", padx=20, pady=16)
        header.pack(fill=tk.X)
        tk.Label(header, text="🌐 MacroWave 全方位更新中心", bg="#0f172a", fg="white", font=("Microsoft JhengHei", 20, "bold")).pack(side=tk.LEFT)
        tk.Button(header, text="開啟隱藏後台", command=lambda: webbrowser.open(DASHBOARD_URL), bg="#2563eb", fg="white", relief=tk.FLAT, padx=14, pady=7).pack(side=tk.RIGHT)

        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)
        run_tab = ttk.Frame(notebook, padding=12)
        settings_tab = ttk.Frame(notebook, padding=12)
        notebook.add(run_tab, text="一鍵更新")
        notebook.add(settings_tab, text="設定")

        card_grid = ttk.Frame(run_tab)
        card_grid.pack(fill=tk.X)
        for index, (name, meta) in enumerate(WORKERS.items()):
            card = ttk.LabelFrame(card_grid, text=meta["title"], padding=10)
            card.grid(row=index // 2, column=index % 2, sticky="nsew", padx=5, pady=5)
            ttk.Checkbutton(card, text="納入一鍵更新", variable=self.worker_vars[name]).pack(anchor=tk.W)
            ttk.Label(card, text=meta["description"], foreground="#475569").pack(anchor=tk.W, pady=(4, 7))
            ttk.Label(card, textvariable=self.status_vars[name], font=("Microsoft JhengHei", 10, "bold")).pack(anchor=tk.W)
        card_grid.columnconfigure(0, weight=1)
        card_grid.columnconfigure(1, weight=1)

        controls = ttk.Frame(run_tab)
        controls.pack(fill=tk.X, pady=10)
        self.run_button = tk.Button(controls, text="🚀 一鍵更新全部", command=self.start_all, bg="#16a34a", fg="white", font=("Microsoft JhengHei", 13, "bold"), relief=tk.FLAT, padx=20, pady=10)
        self.run_button.pack(side=tk.LEFT)
        self.cancel_button = tk.Button(controls, text="停止目前工作", command=self.cancel, state=tk.DISABLED, bg="#dc2626", fg="white", relief=tk.FLAT, padx=14, pady=10)
        self.cancel_button.pack(side=tk.LEFT, padx=8)
        self.progress = ttk.Progressbar(controls, mode="determinate")
        self.progress.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 0))

        self.log = scrolledtext.ScrolledText(run_tab, height=19, state=tk.DISABLED, font=("Consolas", 9), bg="#020617", fg="#d1fae5")
        self.log.pack(fill=tk.BOTH, expand=True)

        self._setting_row(settings_tab, 0, "FRED API Key", self.fred_var, show="•")
        self._setting_row(settings_tab, 1, "上傳 API Key", self.upload_var, show="•")
        ttk.Label(settings_tab, text="共同股票清單（一行一個）").grid(row=2, column=0, sticky="nw", pady=7)
        self.stock_text = scrolledtext.ScrolledText(settings_tab, height=10, width=35)
        self.stock_text.grid(row=2, column=1, sticky="ew", pady=7)
        self.stock_text.insert("1.0", "\n".join(self.config["stock_ids"]))
        ttk.Label(settings_tab, text="本益比基準月份").grid(row=3, column=0, sticky="w", pady=7)
        ttk.Spinbox(settings_tab, from_=1, to=12, textvariable=self.month_var, width=8).grid(row=3, column=1, sticky="w", pady=7)
        ttk.Label(settings_tab, text="股票間等待秒數（最小／最大）").grid(row=4, column=0, sticky="w", pady=7)
        waits = ttk.Frame(settings_tab)
        waits.grid(row=4, column=1, sticky="w", pady=7)
        ttk.Spinbox(waits, from_=0, to=600, textvariable=self.min_wait_var, width=8).pack(side=tk.LEFT)
        ttk.Label(waits, text=" ～ ").pack(side=tk.LEFT)
        ttk.Spinbox(waits, from_=0, to=600, textvariable=self.max_wait_var, width=8).pack(side=tk.LEFT)
        ttk.Checkbutton(settings_tab, text="六大指標與台股資金流向同時同步原有舊站（預設只同步 590bbs）", variable=self.legacy_var).grid(row=5, column=1, sticky="w", pady=7)
        ttk.Button(settings_tab, text="儲存設定", command=self.save_settings).grid(row=6, column=1, sticky="w", pady=15)
        settings_tab.columnconfigure(1, weight=1)

    def _setting_row(self, parent, row, label, variable, show=None):
        ttk.Label(parent, text=label).grid(row=row, column=0, sticky="w", pady=7)
        ttk.Entry(parent, textvariable=variable, show=show or "", width=56).grid(row=row, column=1, sticky="ew", pady=7)

    def current_config(self):
        return normalize_config({
            "fred_api_key": self.fred_var.get(),
            "upload_api_key": self.upload_var.get(),
            "stock_ids": self.stock_text.get("1.0", tk.END),
            "target_month": self.month_var.get(),
            "minimum_wait_seconds": self.min_wait_var.get(),
            "maximum_wait_seconds": self.max_wait_var.get(),
            "sync_legacy_sites": self.legacy_var.get(),
            "selected_workers": [name for name, variable in self.worker_vars.items() if variable.get()],
        })

    def save_settings(self, notify=True):
        try:
            self.config = save_config(self.current_config())
            if notify:
                messagebox.showinfo("設定完成", "設定及各工具相容檔已儲存在 EXE 資料夾。")
            return True
        except Exception as error:
            messagebox.showerror("設定失敗", str(error))
            return False

    def append_log(self, text):
        self.log.config(state=tk.NORMAL)
        self.log.insert(tk.END, text)
        self.log.see(tk.END)
        self.log.config(state=tk.DISABLED)

    def start_all(self):
        if self.running or not self.save_settings(notify=False):
            return
        selected = [name for name, variable in self.worker_vars.items() if variable.get()]
        if not selected:
            messagebox.showwarning("尚未選擇", "至少選擇一項更新工作。")
            return
        self.running = True
        self.run_button.config(state=tk.DISABLED)
        self.cancel_button.config(state=tk.NORMAL)
        self.progress.config(maximum=len(selected), value=0)
        for name in WORKERS:
            self.status_vars[name].set("排隊中" if name in selected else "已略過")
        threading.Thread(target=self._run_sequence, args=(selected,), daemon=True).start()

    def _run_sequence(self, selected):
        logs_dir = app_directory() / "AllInOne_Logs"
        logs_dir.mkdir(exist_ok=True)
        config_path = app_directory() / CONFIG_NAME
        results = {}
        for index, name in enumerate(selected, 1):
            if not self.running:
                results[name] = False
                break
            log_file = logs_dir / f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{name}.log"
            self.events.put(("status", name, "執行中"))
            self.events.put(("log", f"\n===== {WORKERS[name]['title']} =====\n"))
            try:
                command = worker_command(name, config_path, log_file)
                self.current_process = subprocess.Popen(command, cwd=app_directory())
                position = 0
                while self.current_process.poll() is None:
                    position = self._read_log(log_file, position)
                    time.sleep(.35)
                position = self._read_log(log_file, position)
                success = self.current_process.returncode == 0
            except Exception:
                self.events.put(("log", traceback.format_exc()))
                success = False
            finally:
                self.current_process = None
            results[name] = success
            self.events.put(("status", name, "完成" if success else "失敗"))
            self.events.put(("progress", index))
        self.events.put(("finished", results))

    def _read_log(self, path, position):
        if not path.exists():
            return position
        with open(path, "r", encoding="utf-8", errors="replace") as handle:
            handle.seek(position)
            text = handle.read()
            position = handle.tell()
        if text:
            self.events.put(("log", text))
        return position

    def cancel(self):
        self.running = False
        if self.current_process and self.current_process.poll() is None:
            self.current_process.terminate()
        self.append_log("\n使用者已要求停止目前工作。\n")

    def _drain_events(self):
        try:
            while True:
                event = self.events.get_nowait()
                if event[0] == "log": self.append_log(event[1])
                elif event[0] == "status": self.status_vars[event[1]].set(event[2])
                elif event[0] == "progress": self.progress.config(value=event[1])
                elif event[0] == "finished":
                    self.running = False
                    self.run_button.config(state=tk.NORMAL)
                    self.cancel_button.config(state=tk.DISABLED)
                    failed = [WORKERS[name]["title"] for name, success in event[1].items() if not success]
                    if failed: messagebox.showwarning("更新完成", f"完成，但以下工作失敗：{'、'.join(failed)}\n請查看視窗紀錄。")
                    else: messagebox.showinfo("更新完成", "所有選取工作均已完成。")
        except queue.Empty:
            pass
        self.root.after(150, self._drain_events)


def parse_args(argv=None):
    parser = argparse.ArgumentParser(add_help=True)
    parser.add_argument("--worker", choices=WORKERS)
    parser.add_argument("--config")
    parser.add_argument("--log-file")
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    if args.worker:
        handle = redirect_worker_output(args.log_file)
        try:
            run_worker(args.worker, args.config)
            return 0
        except Exception:
            traceback.print_exc()
            return 1
        finally:
            if handle:
                sys.stdout = sys.__stdout__
                sys.stderr = sys.__stderr__
                handle.close()
    os.chdir(app_directory())
    root = tk.Tk()
    AllInOneApp(root)
    root.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
