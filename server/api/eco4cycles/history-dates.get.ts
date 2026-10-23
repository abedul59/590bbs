// server/api/eco4cycles/history-dates.ts
import { defineEventHandler } from 'h3'
import { serverSupabaseClient } from '#supabase/server'
import { readEco4CyclesSnapshot } from '../../utils/eco4cyclesRecords'

export default defineEventHandler(async (event) => {
  const supabase = await serverSupabaseClient(event)

  // 只撈取 date 欄位，並由大到小排序 (新到舊)
  const { data, error } = await supabase
    .from('eco4cycles_economic_records')
    .select('date')
    .order('date', { ascending: false })

  if (!error && data?.length) {
    return { success: true, dates: data.map(d => d.date), source: 'database' }
  }

  const snapshot = await readEco4CyclesSnapshot()
  if (snapshot.length) {
    // 資料表建好但仍為空時，第一次開啟就把舊站快照寫入新表。
    if (!error) await supabase.from('eco4cycles_economic_records').upsert(snapshot, { onConflict: 'date' })
    return { success: true, dates: snapshot.map(record => record.date).sort().reverse(), source: 'migrated-snapshot' }
  }

  return { success: false, error: error?.message || 'Eco4Cycles 尚無歷史資料' }
})
