# Bengo Auto Windows

Bengo 大戶籌碼自動抓取、JSON 備份與 590bbs 同步工具。

目前網站：<https://590bbs.vercel.app/macrowave?view=bengo>

## 使用方式

1. 將 `BengoAuto.exe`、`stock_id_settings.example.csv` 放在同一資料夾。
2. 把清單檔重新命名為 `stock_id_settings.csv`，每行填一個股票代號。
3. 電腦需安裝最新版 Google Chrome 或 Chromium。
4. 執行 `BengoAuto.exe`；Selenium Manager 會自動配對 ChromeDriver。
5. 成功抓取的 JSON 會保存在 `Bengo_JSON_Backups`，同時上傳至 590bbs。

程式同步端點：`https://590bbs.vercel.app/api/bengo/upload`

如需顯示瀏覽器、縮短股票間隔或完成後開啟網站，將
`bengo_settings.example.json` 複製為 `bengo_settings.json` 後調整。
