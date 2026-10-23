import { serverSupabaseClient } from '#supabase/server'
import { readStockDashboardSnapshot, uniqueStockDashboardRecords, type StockDashboardRecord } from '../../utils/stockDashboardRecords'

function newestFirst(left: StockDashboardRecord, right: StockDashboardRecord) {
  return right.data_year - left.data_year || right.data_month - left.data_month
}

export default defineEventHandler(async (event) => {
  const supabase = await serverSupabaseClient(event)
  const { id, year, month } = getQuery(event)
  const { data: databaseRows, error } = await supabase
    .from('stock_dashboard_data')
    .select('*')
    .order('data_year', { ascending: false })
    .order('data_month', { ascending: false })

  let records = (databaseRows || []) as StockDashboardRecord[]
  let source = 'database'
  if (error || !records.length) {
    const snapshot = await readStockDashboardSnapshot()
    const { data: portableRows } = await supabase
      .from('macrowave_dashboard_data')
      .select('content')
      .in('source_type', ['Stock dashboard database migration', 'Stock dashboard upload'])
      .order('created_at', { ascending: true })
    const portableRecords = (portableRows || []).flatMap(row => Array.isArray(row.content?.records) ? row.content.records : []) as StockDashboardRecord[]
    records = uniqueStockDashboardRecords([...snapshot, ...portableRecords])
    source = 'migrated-snapshot'

    if (snapshot.length) {
      if (!error) {
        await supabase.from('stock_dashboard_data').upsert(snapshot, { onConflict: 'stock_id,data_year,data_month' })
      } else {
        const { data: migrationRows } = await supabase
          .from('macrowave_dashboard_data')
          .select('id')
          .eq('source_type', 'Stock dashboard database migration')
          .limit(1)
        if (!migrationRows?.length) {
          await supabase.from('macrowave_dashboard_data').insert({
            source_type: 'Stock dashboard database migration',
            content: { schema: 1, records: snapshot }
          })
        }
      }
    }
  }

  const allRecords = records.sort(newestFirst)
  const filtered = allRecords.filter((record) => {
    if (id && record.stock_id !== String(id)) return false
    if (year && month && id && (record.data_year !== Number(year) || record.data_month !== Number(month))) return false
    return true
  })
  const stockMap = new Map<string, string>()
  for (const record of allRecords) if (!stockMap.has(record.stock_id)) stockMap.set(record.stock_id, record.stock_name)
  const availableStocks = [...stockMap].map(([stockId, name]) => ({ id: stockId, name })).sort((a, b) => a.id.localeCompare(b.id))

  return { currentData: filtered[0] || null, availableStocks, source, migrated_records: source === 'migrated-snapshot' ? allRecords.length : undefined }
})
