import { serverSupabaseClient } from '#supabase/server'

export default defineEventHandler(async (event) => {
  // 檢查 API 密鑰
  const apiKey = getHeader(event, 'x-api-key') || getHeader(event, 'api_key')
  const validKey = process.env.API_UPLOAD_KEY || 'macrowave168'

  if (apiKey !== validKey) {
    throw createError({ statusCode: 403, statusMessage: '密鑰錯誤 (Invalid API Key)' })
  }

  // 讀取傳入的 JSON 數據
  const body = await readBody(event)
  if (!body) {
    throw createError({ statusCode: 400, statusMessage: '未找到有效數據' })
  }

  // 自動判斷來源：如果是 Python 爬蟲推送過來的，User-Agent 通常包含 python-requests
  const userAgent = getHeader(event, 'user-agent') || ''
  const isFromPython = userAgent.toLowerCase().includes('python')
  const sourceType = isFromPython ? 'Render 自動同步' : 'GUI JSON 手動上傳'

  // 整理要存入 Supabase 的格式
  const payload = {
    content: body,
    source_type: sourceType
  }

  // 寫入 Supabase 資料庫的 dashboard_data 資料表
  const client = await serverSupabaseClient(event)
  const { error } = await client
    .from('macrowave_dashboard_data')
    .insert([payload])

  if (error) {
    throw createError({ statusCode: 500, statusMessage: error.message })
  }

  return { status: 'success', message: '資料庫上傳成功' }
})
