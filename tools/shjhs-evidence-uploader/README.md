# SHJHS 輔導錄音自動歸檔工具

Windows GUI 工具，用來一次選取多個 SHJHS 輔導錄音，依每個檔案自己的日期上傳至 Telegram 備份，並在 `590bbs` 的 `evidence_logs.log_date` 建立索引。網站「SHJHS 輔導紀錄中心」月曆會在各自日期顯示錄音證據。

## 日期判斷

每個檔案獨立判斷，優先順序如下：

1. 檔名內的西元日期與時間，例如 `REC_20261123_083045.m4a`、`2026-11-23 08.30.mp3`。
2. Windows 檔案建立時間與修改時間中較早者。錄音被複製到電腦時，建立時間通常會變成複製當下，因此較早的修改時間更接近原始錄音日期。

選檔後，表格會先顯示判定結果與日期來源，再開始上傳。清單會依日期排序，但不會修改原始錄音檔。

## 上傳流程

1. 計算本機 SHA-256。
2. 查詢 `evidence_logs.file_hash`，相同檔案已存在時直接略過。
3. 串流上傳至 SHJHS Render API `/upload/`，不會把整個大檔讀入記憶體。
4. 將 Telegram 連結、訊息編號、檔名、SHA-256 與自動判斷的 `log_date` 寫入 Supabase。
5. 若 Telegram 已成功但 Supabase 暫時失敗，按一次上傳即可只重試資料庫寫入，不會重傳 Telegram。

## 第一次使用

將 `SHJHS_Evidence_Uploader.exe` 放在可寫入的資料夾後開啟，填入：

- SHJHS Render API：預設 `https://five90bbs-telegram-shjhs-api.onrender.com`
- Supabase URL
- Supabase anon key
- SHJHS Telegram Topic ID

按「儲存設定」後，資料會寫入 EXE 同一資料夾的 `shjhs_uploader_config.json`。該檔包含 Supabase key，請勿傳給他人或提交到 Git。若同資料夾已有舊工具的 `config.json`，新版會自動讀取其中的 Supabase URL／Key，但仍需填入 Topic ID。

## 本機建置

```bash
go install github.com/akavel/rsrc@latest
rsrc -manifest app.exe.manifest -o rsrc_windows_amd64.syso
go test ./...
go build -trimpath -ldflags="-H windowsgui -s -w" -o SHJHS_Evidence_Uploader.exe .
```

實際憑證、`config.json`、`session.json` 都不會包進 EXE。
