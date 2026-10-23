# 590bbs

以 Nuxt 建置的班級公告與管理網站。

## Deployment

正式環境由 Vercel 部署；合併至 `main` 分支後會自動建立新的 Production Deployment。

cron-job.org 應每小時呼叫 `https://shjhs-class-system.vercel.app/api/cron-render`。此 Vercel 端點立即回傳 HTTP 204／0 bytes，再使用背景任務喚醒 Render，避免免費 Render 冷啟動時的平台回應被 cron-job.org 判定為 `Response data too big`。不要再將 cron-job.org 直接指向 Render `/run`。

## SHJHS 輔導紀錄整合

後台的「SHJHS 輔導紀錄」分頁整合自 `abedul59/tlogs-shjhs`，包含文字紀錄、月曆查詢、編輯刪除、SHJHS Telegram 錄音保全，以及完整 JSON 備份匯入／匯出。

首次啟用時，請在目標 Supabase SQL Editor 執行：

```text
supabase/migrations/202610210001_create_shjhs_counseling_tables.sql
```

若曾套用較早版本（`message_id` 為唯一值），再執行：

```text
supabase/migrations/202610210002_allow_duplicate_evidence_message_ids.sql
```

若要直接將舊 Supabase 全量搬到目前專案，先使用 `--dry-run` 核對來源筆數，再執行正式轉移：

```bash
SOURCE_SUPABASE_URL=... SOURCE_SUPABASE_KEY=... \
TARGET_SUPABASE_URL=... TARGET_SUPABASE_KEY=... \
npm run migrate:tlogs-shjhs -- --dry-run

SOURCE_SUPABASE_URL=... SOURCE_SUPABASE_KEY=... \
TARGET_SUPABASE_URL=... TARGET_SUPABASE_KEY=... \
npm run migrate:tlogs-shjhs
```

轉移程式會分頁讀取 `counseling_logs` 與 `evidence_logs`，並依原始 `id` upsert；舊錄音流水號會轉為 `legacy:<原始 ID>`，避免和新紀錄衝突，重跑也不會產生重複紀錄。錄音本體保留在原 SHJHS Telegram 群組，轉移的是 Telegram 連結、訊息 ID、檔名與指紋等索引。正式環境可用 `NUXT_PUBLIC_SHJHS_TELEGRAM_API_URL` 覆寫預設 Render API 網址。

## Eco4Cycles 整合與資料遷移

隱藏入口 `/macrowave` 目前可選擇 MacroWave 或 Eco4Cycles。Eco4Cycles 使用隔離的 `eco4cycles_economic_records` 資料表；首次啟用時，請在目標 Supabase SQL Editor 執行：

```text
supabase/migrations/202610230001_create_eco4cycles_records.sql
```

推送到 `main` 後，`Migrate Eco4Cycles history` 工作流程會從原站逐筆匯出歷史紀錄並保存為伺服器快照。新表為空時，第一次開啟 Eco4Cycles 會自動將快照 upsert 進新表；若表尚未建立，畫面仍會由快照提供原有歷史資料。也可手動執行：

```bash
npm run migrate:eco4cycles
```

Look at the [Nuxt documentation](https://nuxt.com/docs/getting-started/introduction) to learn more.

## Setup

Make sure to install dependencies:

```bash
# npm
npm install

# pnpm
pnpm install

# yarn
yarn install

# bun
bun install
```

## Development Server

Start the development server on `http://localhost:3000`:

```bash
# npm
npm run dev

# pnpm
pnpm dev

# yarn
yarn dev

# bun
bun run dev
```

## Production

Build the application for production:

```bash
# npm
npm run build

# pnpm
pnpm build

# yarn
yarn build

# bun
bun run build
```

Locally preview production build:

```bash
# npm
npm run preview

# pnpm
pnpm preview

# yarn
yarn preview

# bun
bun run preview
```

Check out the [deployment documentation](https://nuxt.com/docs/getting-started/deployment) for more information.
"# 590bbs" 
