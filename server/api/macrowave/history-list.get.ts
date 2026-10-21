import { serverSupabaseClient } from '#supabase/server'

export default defineEventHandler(async (event) => {
  const client = await serverSupabaseClient(event)
  const { data, error } = await client
    .from('macrowave_dashboard_data')
    .select('id, created_at, source_type')
    .order('created_at', { ascending: false })
    .limit(100)

  if (error) return { success: false, message: error.message, data: [] }

  return {
    success: true,
    data: (data || []).map((row) => ({
      filename: String(row.id),
      label: `${new Date(row.created_at).toLocaleString('zh-TW', { timeZone: 'Asia/Taipei' })} · ${row.source_type || '資料更新'}`
    }))
  }
})
