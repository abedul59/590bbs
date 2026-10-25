import { serverSupabaseClient } from '#supabase/server'

const cleanInt = (value: unknown) => Number.parseInt(String(value ?? '').replace(/,/g, ''), 10) || 0
const cleanFloat = (value: unknown) => Number.parseFloat(String(value ?? '').replace(/,/g, '').replace('%', '')) || 0

const normalizeDate = (value: unknown) => {
  const raw = String(value ?? '').split('.')[0].trim()
  if (/^\d{4}-\d{2}-\d{2}$/.test(raw)) return raw
  if (/^\d{8}$/.test(raw)) return `${raw.slice(0, 4)}-${raw.slice(4, 6)}-${raw.slice(6, 8)}`
  return ''
}

export default defineEventHandler(async (event) => {
  const body = await readBody<Record<string, any>>(event)
  const stockId = String(body?.stock_id || '').trim()
  const stockName = String(body?.stock_name || '').trim()
  const history = Array.isArray(body?.history) ? body.history : []
  if (!/^[A-Za-z0-9]{2,12}$/.test(stockId)) {
    throw createError({ statusCode: 400, statusMessage: '股票代碼格式不正確' })
  }
  if (!history.length || history.length > 5000) {
    throw createError({ statusCode: 400, statusMessage: 'history 必須包含 1 至 5000 筆資料' })
  }

  const records = history.map(row => ({
    stock_id: stockId,
    stock_name: stockName,
    date: normalizeDate(row.date),
    price: cleanFloat(row.price),
    total_shares: cleanInt(row.total_shares),
    total_people: cleanInt(row.total_people || row.total_ppl),
    bengo_threshold: String(row.bengo_threshold || row.threshold_str || ''),
    major_people: cleanInt(row.major_people || row.major_ppl),
    major_pct: cleanFloat(row.major_pct),
    note: String(row.note || '')
  })).filter(row => row.date)

  if (!records.length) throw createError({ statusCode: 400, statusMessage: '沒有有效日期的資料可匯入' })

  const supabase = await serverSupabaseClient(event)
  const { error } = await supabase.from('stock_data').upsert(records, { onConflict: 'stock_id,date' })
  if (!error) return { success: true, count: records.length, storage: 'database' }

  const { error: portableError } = await supabase.from('macrowave_dashboard_data').insert({
    source_type: 'Bengo stock data',
    content: { schema: 1, stock_id: stockId, stock_name: stockName, history: records }
  })
  if (portableError) throw createError({ statusCode: 500, statusMessage: portableError.message })
  return { success: true, count: records.length, storage: 'portable-database' }
})
