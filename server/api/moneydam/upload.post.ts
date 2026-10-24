import { serverSupabaseClient } from '#supabase/server'

export default defineEventHandler(async (event) => {
  const body = await readBody<{ timestamp?: string, content?: string }>(event)
  const timestamp = String(body?.timestamp || '').trim()
  const content = String(body?.content || '').trim()
  if (!timestamp || !content) throw createError({ statusCode: 400, statusMessage: 'JSON 必須包含 timestamp 與 content' })

  const supabase = await serverSupabaseClient(event)
  const { error } = await supabase.from('analyses').insert({ timestamp, content })
  if (!error) return { success: true, storage: 'database' }

  const { error: portableError } = await supabase.from('macrowave_dashboard_data').insert({
    source_type: 'Moneydam analysis', content: { schema: 1, timestamp, content }
  })
  if (portableError) throw createError({ statusCode: 500, statusMessage: portableError.message })
  return { success: true, storage: 'portable-database' }
})
