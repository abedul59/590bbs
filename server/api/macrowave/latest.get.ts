import { serverSupabaseClient } from '#supabase/server'

export default defineEventHandler(async (event) => {
  const client = await serverSupabaseClient(event)
  
  // 抓取 created_at 最新的一筆資料
  const { data, error } = await client
    .from('macrowave_dashboard_data')
    .select('*')
    .order('created_at', { ascending: false })
    .limit(1)
    .single()

  if (error || !data) {
    return { data: null }
  }

  return { data }
})
