import { serverSupabaseClient } from '#supabase/server'

type TrackerContent = {
  date: string
  stats: any[]
  top30: any[]
}

export default defineEventHandler(async (event) => {
  const supabase = await serverSupabaseClient(event)
  const requestedDate = String(getQuery(event).date || '')

  const [{ data: nativeDates }, { data: portableRows }] = await Promise.all([
    supabase.from('category_stats').select('date'),
    supabase.from('macrowave_dashboard_data').select('content').eq('source_type', 'Twstock tracker record').order('created_at', { ascending: false })
  ])

  const portable = (portableRows || []).map(row => row.content as TrackerContent).filter(row => row?.date)
  const availableDates = [...new Set([
    ...(nativeDates || []).map(row => String(row.date)),
    ...portable.map(row => String(row.date))
  ])].sort((left, right) => right.localeCompare(left))

  const selectedDate = requestedDate || availableDates[0] || ''
  let stats: any[] = []
  let top30: any[] = []
  let source = 'database'

  if (selectedDate) {
    const [{ data: nativeStats, error: statsError }, { data: nativeTop30, error: top30Error }] = await Promise.all([
      supabase.from('category_stats').select('*').eq('date', selectedDate),
      supabase.from('daily_top30').select('*').eq('date', selectedDate).order('rank', { ascending: true })
    ])
    stats = nativeStats || []
    top30 = nativeTop30 || []

    if (statsError || top30Error || !stats.length || !top30.length) {
      const fallback = portable.find(row => String(row.date) === selectedDate)
      stats = fallback?.stats || []
      top30 = fallback?.top30 || []
      source = fallback ? 'portable-database' : 'database'
    }
  }

  stats.sort((left, right) => {
    const leftValue = Number.parseFloat(String(left.avg_change_pct || '').replace('%', '').replace('+', '')) || 0
    const rightValue = Number.parseFloat(String(right.avg_change_pct || '').replace('%', '').replace('+', '')) || 0
    return rightValue - leftValue
  })
  top30.sort((left, right) => Number(left.rank || 0) - Number(right.rank || 0))

  return { availableDates, selectedDate, stats, top30, source }
})
