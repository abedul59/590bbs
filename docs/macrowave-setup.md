# MacroWave 獨立戰情室設定

MacroWave 使用獨立網址 `/macrowave`。管理員可從 `/admin` 按「系統狀態正常」並再次輸入密碼進入；通過驗證後重新整理仍會停留在 `/macrowave`，不會返回後台。

## Supabase

先在目前網站使用的 Supabase SQL Editor 執行：

`supabase/migrations/202610210003_create_macrowave_tables.sql`

這會建立獨立的 `macrowave_*` 資料表，避免和公告網站原有資料表互相影響。

## Vercel 環境變數

一般查詢、圖表及手動資料管理沿用現有 `SUPABASE_URL`、`SUPABASE_KEY`。

若要啟用 Render 爬蟲同步，再設定：

- `NUXT_PUBLIC_MACROWAVE_SYNC_API_URLS`：一個或多個 Render 服務根網址，多個網址以逗號分隔。
- `NUXT_PUBLIC_MACROWAVE_TWSTOCK_SYNC_API_URL`：台股同步 Render 服務根網址。
- `API_UPLOAD_KEY`：Render 同步程式呼叫 MacroWave 上傳 API 時使用的金鑰。

同步資料上傳端點是 `/api/macrowave/upload`，請在要求標頭送出 `X-Api-Key`。
