import { serverSupabaseClient } from '#supabase/server'

export default defineEventHandler(async (event) => {
  const expectedToken = process.env.TWSTOCK_SYNC_TOKEN || process.env.API_SYNC_TOKEN || 'macrowave168'
  const authorization = getHeader(event, 'authorization') || ''
  if (authorization !== `Bearer ${expectedToken}`) {
    throw createError({ statusCode: 401, statusMessage: '身分驗證失敗' })
  }

  const body = await readBody<Record<string, any>>(event)
  const date = String(body?.date || '').trim()
  const stats = Array.isArray(body?.yahoo_stats) ? body.yahoo_stats : []
  const top30 = Array.isArray(body?.yahoo_top30) ? body.yahoo_top30 : []
  if (!/^\d{8}(\d{6})?$/.test(date)) throw createError({ statusCode: 400, statusMessage: 'date 必須是 YYYYMMDD 或 YYYYMMDDhhmmss' })
  if (!stats.length && !top30.length) throw createError({ statusCode: 400, statusMessage: '缺少 yahoo_stats 與 yahoo_top30 資料' })

  const statsPayload = stats.map(row => ({
    date, market: row.market, category: row.category,
    avg_change_pct: row.avg_change_pct, avg_price: row.avg_price, avg_vol: row.avg_vol
  }))
  const top30Payload = top30.map(row => ({
    date, rank: row.rank, ticker: String(row.ticker || ''), name: row.name,
    market: row.market, total_value: row.total_value
  }))

  const supabase = await serverSupabaseClient(event)
  const deleteStats = await supabase.from('category_stats').delete().eq('date', date)
  const deleteTop30 = await supabase.from('daily_top30').delete().eq('date', date)
  const insertStats = statsPayload.length ? await supabase.from('category_stats').insert(statsPayload) : { error: null }
  const insertTop30 = top30Payload.length ? await supabase.from('daily_top30').insert(top30Payload) : { error: null }

  if (!deleteStats.error && !deleteTop30.error && !insertStats.error && !insertTop30.error) {
    return { success: true, storage: 'native-tables', message: `成功同步 ${date} 的資料` }
  }

  const { error } = await supabase.from('macrowave_dashboard_data').insert({
    source_type: 'Twstock tracker record',
    content: { schema: 1, date, stats: statsPayload, top30: top30Payload, uploaded_by: 'desktop-exe' }
  })
  if (error) throw createError({ statusCode: 500, statusMessage: error.message })
  return { success: true, storage: 'portable-database', message: `成功同步 ${date} 的資料` }
})
