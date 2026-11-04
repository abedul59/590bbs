import { serverSupabaseClient } from '#supabase/server'
import { isMacrowaveContent, MACROWAVE_SOURCE_TYPES } from '../../utils/macrowaveRecords'

export default defineEventHandler(async (event) => {
  const client = await serverSupabaseClient(event)
  
  // 共用備援表也保存 Bengo、台股資金流向等資料；只讀取 MacroWave 紀錄。
  const { data, error } = await client
    .from('macrowave_dashboard_data')
    .select('*')
    .in('source_type', [...MACROWAVE_SOURCE_TYPES])
    .order('created_at', { ascending: false })
    .limit(50)

  const latest = (data || []).find(row => isMacrowaveContent(row.content))
  if (error || !latest) {
    return { data: null }
  }

  return { data: latest }
})
