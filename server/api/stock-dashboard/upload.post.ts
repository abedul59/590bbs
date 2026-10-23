import { serverSupabaseClient } from '#supabase/server'

export default defineEventHandler(async (event) => {
  const supabase = await serverSupabaseClient(event)
  const body = await readBody<Record<string, any>>(event)
  if (!body || typeof body !== 'object' || Array.isArray(body)) {
    throw createError({ statusCode: 400, statusMessage: 'JSON 格式錯誤' })
  }

  const now = new Date()
  const records = Object.entries(body).map(([stockId, content]) => {
    const meta = content?.Meta || {}
    return {
      stock_id: stockId,
      stock_name: meta.StockName || stockId,
      data_year: Number.parseInt(meta.QueryDate?.split('-')[0]) || now.getFullYear(),
      data_month: Number.parseInt(meta.TargetMonth) || now.getMonth() + 1,
      raw_data: content,
      update_date: now.toISOString()
    }
  })

  const { error } = await supabase.from('stock_dashboard_data').upsert(records, { onConflict: 'stock_id,data_year,data_month' })
  if (error) {
    const { error: portableError } = await supabase.from('macrowave_dashboard_data').insert({
      source_type: 'Stock dashboard upload',
      content: { schema: 1, records }
    })
    if (portableError) throw createError({ statusCode: 500, statusMessage: portableError.message })
  }

  return { success: true, message: `成功匯入 ${records.length} 筆資料！`, storage: error ? 'portable-database' : 'stock-dashboard-database' }
})
