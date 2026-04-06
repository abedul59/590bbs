import { serverSupabaseClient } from '#supabase/server'

export default defineEventHandler(async (event) => {
  try {
    // 取得 Supabase 連線
    const supabase = await serverSupabaseClient(event)
    
    // 取得使用者的真實 IP 與設備資訊 (相容 Vercel 的 headers)
    const headers = getRequestHeaders(event)
    const ip = headers['x-forwarded-for'] || headers['x-real-ip'] || '無法取得 IP'
    const userAgent = headers['user-agent'] || '未知設備'

    // 寫入到我們剛剛確認好的資料庫表格中
    const { error } = await supabase.from('visitor_logs').insert([
      { ip_address: ip, user_agent: userAgent }
    ])

    if (error) {
      console.error('寫入訪客紀錄失敗:', error)
      return { success: false, error: error.message }
    }

    return { success: true }
  } catch (error: any) {
    console.error('伺服器 API 錯誤:', error)
    return { success: false, error: error.message || '伺服器錯誤' }
  }
})
