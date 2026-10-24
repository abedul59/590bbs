import { serverSupabaseClient } from '#supabase/server'

const ENDPOINT = 'https://lawxstudents168-moneydam-scraper-api.hf.space/api/scrape'

export default defineEventHandler(async (event) => {
  let result: any
  try {
    result = await $fetch(ENDPOINT, { timeout: 60000 })
  } catch (error: any) {
    throw createError({ statusCode: 502, statusMessage: `Moneydam 爬蟲無回應：${error?.message || error}` })
  }
  if (!result?.timestamp || !result?.content) throw createError({ statusCode: 502, statusMessage: 'Moneydam 爬蟲回傳格式錯誤' })

  const supabase = await serverSupabaseClient(event)
  const { error } = await supabase.from('analyses').insert({ timestamp: result.timestamp, content: result.content })
  let storage = 'database'
  if (error) {
    storage = 'portable-database'
    const { error: portableError } = await supabase.from('macrowave_dashboard_data').insert({
      source_type: 'Moneydam analysis',
      content: { schema: 1, timestamp: result.timestamp, content: result.content, endpoint: ENDPOINT }
    })
    if (portableError) throw createError({ statusCode: 500, statusMessage: portableError.message })
  }
  return { success: true, timestamp: result.timestamp, content: result.content, storage }
})
