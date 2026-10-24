import { serverSupabaseClient } from '#supabase/server'

export default defineEventHandler(async (event) => {
  const supabase = await serverSupabaseClient(event)
  const [{ data: nativeRows }, { data: portableRows }] = await Promise.all([
    supabase.from('analyses').select('id,timestamp,content,created_at').order('created_at', { ascending: false }),
    supabase.from('macrowave_dashboard_data').select('id,content,created_at').eq('source_type', 'Moneydam analysis').order('created_at', { ascending: false })
  ])

  const records = [
    ...(nativeRows || []).map(row => ({ ...row, id: `native-${row.id}`, source: 'database' })),
    ...(portableRows || []).map(row => ({
      id: `portable-${row.id}`,
      timestamp: row.content?.timestamp || row.created_at,
      content: row.content?.content || '',
      created_at: row.created_at,
      source: 'portable-database'
    }))
  ].filter(row => row.content).sort((left, right) => String(right.created_at || right.timestamp).localeCompare(String(left.created_at || left.timestamp)))

  return { records }
})
