import { serverSupabaseClient } from '#supabase/server'
import { isMacrowaveContent, MACROWAVE_SOURCE_TYPES } from '../../utils/macrowaveRecords'

export default defineEventHandler(async (event) => {
  const id = String(getQuery(event).file || '')
  if (!id) throw createError({ statusCode: 400, statusMessage: '缺少歷史資料 ID' })

  const client = await serverSupabaseClient(event)
  const { data, error } = await client
    .from('macrowave_dashboard_data')
    .select('*')
    .eq('id', id)
    .in('source_type', [...MACROWAVE_SOURCE_TYPES])
    .single()

  if (error || !data || !isMacrowaveContent(data.content)) {
    throw createError({ statusCode: 404, statusMessage: '找不到 MacroWave 歷史資料' })
  }
  return { data }
})
