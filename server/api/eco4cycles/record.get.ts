// server/api/eco4cycles/record.ts
import { defineEventHandler, getQuery } from 'h3'
import { serverSupabaseClient } from '#supabase/server'
import { readEco4CyclesSnapshot } from '../../utils/eco4cyclesRecords'

export default defineEventHandler(async (event) => {
  const query = getQuery(event)
  const date = query.date as string

  if (!date) {
    return { success: false, error: '缺少日期參數' }
  }

  const supabase = await serverSupabaseClient(event)

  // 撈取符合該日期的單筆完整紀錄
  const { data, error } = await supabase
    .from('eco4cycles_economic_records')
    .select('*')
    .eq('date', date)
    .single()

  if (!error && data) {
    return { success: true, data, source: 'database' }
  }

  const snapshot = await readEco4CyclesSnapshot()
  const migratedRecord = snapshot.find(record => record.date === date)
  if (migratedRecord) return { success: true, data: migratedRecord, source: 'migrated-snapshot' }

  return { success: false, error: error?.message || '找不到指定日期的紀錄' }
})
