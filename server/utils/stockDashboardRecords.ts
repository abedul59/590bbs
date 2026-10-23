export interface StockDashboardRecord {
  stock_id: string
  stock_name: string
  data_year: number
  data_month: number
  update_date?: string
  raw_data: Record<string, unknown>
}

export async function readStockDashboardSnapshot(): Promise<StockDashboardRecord[]> {
  const value = await useStorage('assets:server').getItem<StockDashboardRecord[]>('stock-dashboard-records.json')
  return Array.isArray(value) ? value : []
}

export function uniqueStockDashboardRecords(records: StockDashboardRecord[]) {
  const unique = new Map<string, StockDashboardRecord>()
  for (const record of records) {
    const key = `${record.stock_id}:${record.data_year}:${record.data_month}`
    const current = unique.get(key)
    if (!current || String(record.update_date || '') > String(current.update_date || '')) unique.set(key, record)
  }
  return [...unique.values()]
}
