import { writeFile } from 'node:fs/promises'

const sourceBase = (process.env.ECO4CYCLES_SOURCE_URL || 'https://eco4cycles-nuxt.vercel.app').replace(/\/$/, '')
const outputPath = new URL('../server/assets/eco4cycles-records.json', import.meta.url)

async function fetchJson(path) {
  const response = await fetch(`${sourceBase}${path}`, {
    headers: { accept: 'application/json', 'user-agent': '590bbs-eco4cycles-migrator/1.0' }
  })
  if (!response.ok) throw new Error(`${path} 回傳 HTTP ${response.status}`)
  return response.json()
}

const history = await fetchJson('/api/history-dates')
if (!history.success || !Array.isArray(history.dates)) {
  throw new Error(history.error || '舊站沒有回傳日期清單')
}

const records = []
for (let index = 0; index < history.dates.length; index += 8) {
  const dates = history.dates.slice(index, index + 8)
  const batch = await Promise.all(dates.map(async (date) => {
    const response = await fetchJson(`/api/record?date=${encodeURIComponent(date)}`)
    if (!response.success || !response.data) throw new Error(`${date}: ${response.error || '沒有資料'}`)
    const { created_at, updated_at, id, ...record } = response.data
    return record
  }))
  records.push(...batch)
}

records.sort((left, right) => right.date.localeCompare(left.date))
await writeFile(outputPath, `${JSON.stringify(records, null, 2)}\n`, 'utf8')
console.log(`已從 ${sourceBase} 遷移 ${records.length} 筆 Eco4Cycles 紀錄。`)
