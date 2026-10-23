import { readFile, writeFile } from 'node:fs/promises'

const indicatorPath = new URL('../public/macrowave-leading-indicators.json', import.meta.url)
const outputPath = new URL('../public/macrowave-lead-data.json', import.meta.url)
const indicators = JSON.parse(await readFile(indicatorPath, 'utf8'))

const period1 = Math.floor(new Date('2009-01-01T00:00:00Z').getTime() / 1000)
const period2 = Math.floor(Date.now() / 1000)
const yahooUrl = new URL('https://query1.finance.yahoo.com/v8/finance/chart/0050.TW')
yahooUrl.search = new URLSearchParams({
  period1: String(period1),
  period2: String(period2),
  interval: '1mo',
  events: 'history',
  includeAdjustedClose: 'true'
}).toString()

const response = await fetch(yahooUrl, {
  headers: { 'User-Agent': 'Mozilla/5.0 MacroWave data updater' }
})
if (!response.ok) throw new Error(`Yahoo Finance HTTP ${response.status}`)

const payload = await response.json()
const result = payload?.chart?.result?.[0]
const timestamps = result?.timestamp || []
const closes = result?.indicators?.quote?.[0]?.close || []
const pricesByPeriod = new Map()

timestamps.forEach((timestamp, index) => {
  const close = Number(closes[index])
  if (!Number.isFinite(close)) return
  pricesByPeriod.set(new Date(timestamp * 1000).toISOString().slice(0, 7), close)
})

const combined = indicators
  .map(item => ({
    date: `${item.period}-01`,
    close: pricesByPeriod.get(item.period),
    lead: Number(item.lead),
    score: Number(item.score)
  }))
  .filter(item => Number.isFinite(item.close))

if (combined.length < 180) {
  throw new Error(`Only ${combined.length} aligned monthly rows were generated`)
}

await writeFile(outputPath, `${JSON.stringify(combined)}\n`, 'utf8')
console.log(`Generated ${combined.length} monthly rows at ${outputPath.pathname}`)
