import { writeFile } from 'node:fs/promises'

const sourceBase = (process.env.STOCK_DASHBOARD_SOURCE_URL || 'https://stock-dashboard-nuxt.vercel.app').replace(/\/$/, '')
const outputPath = new URL('../server/assets/stock-dashboard-records.json', import.meta.url)

async function fetchJson(path, attempts = 3) {
  let lastError
  for (let attempt = 1; attempt <= attempts; attempt++) {
    try {
      const response = await fetch(`${sourceBase}${path}`, {
        headers: { accept: 'application/json', 'user-agent': '590bbs-stock-dashboard-migrator/1.0' }
      })
      if (!response.ok) throw new Error(`HTTP ${response.status}`)
      return await response.json()
    } catch (error) {
      lastError = error
      if (attempt < attempts) await new Promise(resolve => setTimeout(resolve, attempt * 750))
    }
  }
  throw new Error(`${path}: ${lastError?.message || '讀取失敗'}`)
}

function normalize(record) {
  if (!record?.stock_id || !record.raw_data) return null
  return {
    stock_id: String(record.stock_id),
    stock_name: record.stock_name || String(record.stock_id),
    data_year: Number(record.data_year),
    data_month: Number(record.data_month),
    update_date: record.update_date || new Date().toISOString(),
    raw_data: record.raw_data
  }
}

const index = await fetchJson('/api/stock')
const stocks = Array.isArray(index.availableStocks) ? index.availableStocks : []
const requests = []
for (const stock of stocks) {
  requests.push(`/api/stock?id=${encodeURIComponent(stock.id)}`)
  // 原介面從 2026 年啟用；未來年份不可能已有歷史紀錄，避免對舊站產生大量空查詢。
  for (let year = 2026; year <= new Date().getUTCFullYear(); year++) {
    for (let month = 1; month <= 12; month++) {
      requests.push(`/api/stock?id=${encodeURIComponent(stock.id)}&year=${year}&month=${month}`)
    }
  }
}

const records = new Map()
const initialRecord = normalize(index.currentData)
if (initialRecord) records.set(`${initialRecord.stock_id}:${initialRecord.data_year}:${initialRecord.data_month}`, initialRecord)

for (let offset = 0; offset < requests.length; offset += 16) {
  const batch = await Promise.all(requests.slice(offset, offset + 16).map(path => fetchJson(path)))
  for (const response of batch) {
    const record = normalize(response.currentData)
    if (record) records.set(`${record.stock_id}:${record.data_year}:${record.data_month}`, record)
  }
  console.log(`已掃描 ${Math.min(offset + 16, requests.length)} / ${requests.length} 個歷史查詢。`)
}

const output = [...records.values()].sort((left, right) =>
  left.stock_id.localeCompare(right.stock_id) || right.data_year - left.data_year || right.data_month - left.data_month
)
await writeFile(outputPath, `${JSON.stringify(output, null, 2)}\n`, 'utf8')
console.log(`已從 ${sourceBase} 遷移 ${output.length} 筆、${stocks.length} 檔股票資料。`)
