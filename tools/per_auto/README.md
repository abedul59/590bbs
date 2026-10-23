# PER Auto Windows

台股六大指標與本益比區間資料抓取工具。資料會同步到：

- 590bbs「總大六大指標和本益比區間分析」
- 原 Stock Dashboard（相容保留）

儀表板：<https://590bbs.vercel.app/macrowave?view=stock-dashboard>

## 使用方式

1. 下載 `PER_Auto.exe`。
2. 將 `stock_id_settings.example.csv` 複製並改名為 `stock_id_settings.csv`，與 EXE 放在同一個資料夾。
3. 在 CSV 中一行填一個股票代碼（可保留第一行 `stock_id`）。
4. 雙擊 EXE，輸入 1 到 12 的分析月份。
5. 程式會在同一資料夾留下 JSON，並將結果同步到兩個網站。

若任一網站暫時無法連線，程式會自動重試三次，並繼續同步另一個網站。大量股票之間會隨機等待 40 到 120 秒，以降低來源網站封鎖風險。
