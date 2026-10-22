# MacroWave Windows 自動同步工具

## 使用方法

1. 安裝或更新 Google Chrome。
2. 建議將 `macrowave_config.example.json` 複製並改名為 `macrowave_config.json`（新版也能直接讀取已填寫的 example 檔）。
3. 在 JSON 中使用 `fred_api_key` 或 `FRED_API_KEY` 填入 FRED API Key。
4. 將設定檔放在 `MacroWave_AutoSync.exe` 相同資料夾。
5. 雙擊 `MacroWave_AutoSync.exe`。

工具會產生一份本機 JSON，並依序更新：

- 原 MacroWave Vercel：`https://macrowave-nuxt.vercel.app/api/upload/`
- 590bbs MacroWave：`https://590bbs.vercel.app/api/macrowave/upload`
- 原 MacroWave Render：`https://macrowave-web.onrender.com/api/upload/`

其中一個網站失敗時，程式仍會繼續更新其他網站。免費 Render 冷啟動需要等待約 70 秒。

也可以用 Windows 環境變數 `FRED_API_KEY` 與 `MACROWAVE_API_KEY` 取代設定檔，環境變數的優先權較高。

啟動時主控台會顯示實際讀取的設定檔路徑，但不會顯示 API Key 內容。若未找到 Key，程式會列出所有搜尋位置；同時支援 EXE 所在目錄與目前啟動目錄。

## 從原始碼建置

Windows PowerShell：

```powershell
cd tools/macrowave_autosync
py -m pip install -r requirements-autosync.txt pyinstaller==6.18.0
pyinstaller --noconfirm --clean --onefile --console --name MacroWave_AutoSync --collect-all pandas --collect-all selenium --collect-all webdriver_manager MacroWave_AutoSync.py
```

成品位於 `dist/MacroWave_AutoSync.exe`。
