import { serverSupabaseClient } from '#supabase/server'

const ENDPOINTS = [
  'https://pyfbsdk59-twstock-tracker-api.hf.space/api/scrape',
  'https://lawxstudents168-twstock-tracker-api.hf.space/api/scrape',
  'https://igveri59-twstock-tracker-api.hf.space/api/scrape'
]

export default defineEventHandler(async (event) => {
  let result: any = null
  let endpoint = ''
  let lastError = '未知錯誤'

  for (const url of ENDPOINTS) {
    try {
      const response: any = await $fetch(url, { timeout: 60000 })
      if (response?.date) {
        result = response
        endpoint = url
        break
      }
    } catch (error: any) {
      lastError = error?.message || String(error)
    }
  }

  if (!result) throw createError({ statusCode: 502, statusMessage: `所有爬蟲端點均無回應：${lastError}` })

  const date = String(result.date)
  const stats = Array.isArray(result.yahoo_stats) ? result.yahoo_stats : []
  const top30 = Array.isArray(result.yahoo_top30) ? result.yahoo_top30 : []
  const supabase = await serverSupabaseClient(event)
  let storage = 'native-tables'

  const statsPayload = stats.map((row: any) => ({
    date, market: row.market, category: row.category,
    avg_change_pct: row.avg_change_pct, avg_price: row.avg_price, avg_vol: row.avg_vol
  }))
  const top30Payload = top30.map((row: any) => ({
    date, rank: row.rank, ticker: row.ticker, name: row.name,
    market: row.market, total_value: row.total_value
  }))

  const deleteStats = await supabase.from('category_stats').delete().eq('date', date)
  const deleteTop30 = await supabase.from('daily_top30').delete().eq('date', date)
  const insertStats = statsPayload.length ? await supabase.from('category_stats').insert(statsPayload) : { error: null }
  const insertTop30 = top30Payload.length ? await supabase.from('daily_top30').insert(top30Payload) : { error: null }

  if (deleteStats.error || deleteTop30.error || insertStats.error || insertTop30.error) {
    storage = 'portable-database'
    const { error } = await supabase.from('macrowave_dashboard_data').insert({
      source_type: 'Twstock tracker record',
      content: { schema: 1, date, stats: statsPayload, top30: top30Payload, endpoint }
    })
    if (error) throw createError({ statusCode: 500, statusMessage: error.message })
  }

  return { success: true, message: `雲端同步完成！資料時間：${date}`, date, endpoint, storage }
})
