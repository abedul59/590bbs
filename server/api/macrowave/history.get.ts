import { serverSupabaseClient } from '#supabase/server'

export default defineEventHandler(async (event) => {
  const id = String(getQuery(event).file || '')
  if (!id) throw createError({ statusCode: 400, statusMessage: '缺少歷史資料 ID' })

  const client = await serverSupabaseClient(event)
  const { data, error } = await client
    .from('macrowave_dashboard_data')
    .select('*')
    .eq('id', id)
    .single()

  if (error || !data) throw createError({ statusCode: 404, statusMessage: '找不到歷史資料' })
  return { data }
})
