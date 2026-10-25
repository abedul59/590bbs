import { serverSupabaseClient } from '#supabase/server'

type BengoRecord = {
  stock_id: string
  stock_name: string
  date: string
  price: number
  total_shares: number
  total_people: number
  bengo_threshold: string
  major_people: number
  major_pct: number
  note: string
}

const recordKey = (row: Partial<BengoRecord>) => `${row.stock_id || ''}:${row.date || ''}`

export default defineEventHandler(async (event) => {
  const stockId = String(getQuery(event).stock_id || '').trim()
  const supabase = await serverSupabaseClient(event)

  const [nativeResult, summaryResult, portableResult] = await Promise.all([
    stockId
      ? supabase.from('stock_data').select('*').eq('stock_id', stockId).order('date', { ascending: false })
      : Promise.resolve({ data: [], error: null }),
    supabase.from('stock_summary').select('*').order('stock_id', { ascending: true }),
    supabase.from('macrowave_dashboard_data').select('content,created_at').eq('source_type', 'Bengo stock data').order('created_at', { ascending: false })
  ])

  const portableRecords = (portableResult.data || [])
    .flatMap(row => Array.isArray(row.content?.history) ? row.content.history : []) as BengoRecord[]
  const nativeRecords = (nativeResult.data || []) as BengoRecord[]
  const combined = [...nativeRecords, ...portableRecords]
    .filter(row => !stockId || String(row.stock_id) === stockId)

  const records = [...new Map(combined.map(row => [recordKey(row), row])).values()]
    .sort((left, right) => String(right.date).localeCompare(String(left.date)))

  let nativeSummaryRows: any[] = []
  if (summaryResult.error || !summaryResult.data?.length) {
    const { data } = await supabase
      .from('stock_data')
      .select('stock_id,stock_name,date')
      .order('date', { ascending: false })
    nativeSummaryRows = data || []
  }

  const summaryRows = [
    ...(summaryResult.data || []).map(row => ({
      stock_id: String(row.stock_id),
      stock_name: String(row.stock_name || ''),
      latest_date: String(row.latest_date || row.date || '')
    })),
    ...nativeSummaryRows.map(row => ({
      stock_id: String(row.stock_id),
      stock_name: String(row.stock_name || ''),
      latest_date: String(row.date || '')
    })),
    ...portableRecords.map(row => ({
      stock_id: String(row.stock_id),
      stock_name: String(row.stock_name || ''),
      latest_date: String(row.date || '')
    }))
  ].sort((left, right) => right.latest_date.localeCompare(left.latest_date))
  const summary = [...new Map(summaryRows.map(row => [row.stock_id, row])).values()]
    .sort((left, right) => left.stock_id.localeCompare(right.stock_id))

  return {
    records,
    summary,
    source: nativeResult.error ? 'portable-database' : 'database'
  }
})
