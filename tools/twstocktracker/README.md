# TwStockTracker Windows

台股類股、個股、成交額 Top 30 與資金流向桌面爬蟲。

目前網站：<https://590bbs.vercel.app/macrowave?view=twstocktracker>

## 使用方式

1. 下載 `TwStockTracker.exe`。
2. 執行後先在「每日收盤數據」抓取證交所類股資料。
3. 至「個股詳細數據」抓取 Yahoo 三市場個股資料。
4. 點擊「一鍵儲存 JSON 並推送到 Nuxt 網站」。
5. JSON 會保留在自行選擇的位置，資料同時同步至 590bbs；預設亦同步原 TwStockTracker 網站。

同一天每次匯出都使用 `YYYYMMDDhhmmss` 時間戳記，因此不會互相覆蓋。

## 設定檔

如需變更相容 Token 或關閉舊站同步，將 `stock_tracker_settings.example.json` 複製為 `stock_tracker_settings.json`，並與 EXE 放在同一資料夾。

```json
{
  "api_token": "macrowave168",
  "sync_original_site": true
}
```

新站同步 API：`https://590bbs.vercel.app/api/twstocktracker/sync`

程式會為每個網站重試三次；其中一站失敗不會阻擋另一站，也不影響本機 JSON。
