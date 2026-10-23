// server/api/eco4cycles/chart.ts
import { defineEventHandler, getQuery } from 'h3'

export default defineEventHandler(async (event) => {
  const query = getQuery(event)
  const seriesId = query.seriesId as string
  const days = Number(query.days) || 1825 // 預設抓過去 5 年 (1825天)

  if (!seriesId) return { success: false, error: '缺少指標 ID' }

  const apiKey = process.env.FRED_API_KEY
  if (!apiKey) return { success: false, error: '伺服器尚未設定 FRED_API_KEY' }
  const startDate = new Date()
  startDate.setDate(startDate.getDate() - days)
  const startStr = startDate.toISOString().split('T')[0]

  try {
    const url = `https://api.stlouisfed.org/fred/series/observations?series_id=${seriesId}&api_key=${apiKey}&file_type=json&observation_start=${startStr}`
    const response = await fetch(url)
    const data = await response.json()
    if (!response.ok || !Array.isArray(data.observations)) {
      return { success: false, error: data?.error_message || 'FRED API 回傳格式錯誤' }
    }

    // 清洗資料：過濾空值並分離出 X軸(時間) 與 Y軸(數值)
    const observations = data.observations.filter((obs: any) => obs.value !== '.')
    const labels = observations.map((obs: any) => obs.date)
    const values = observations.map((obs: any) => parseFloat(obs.value))

    return { success: true, labels, values }
  } catch (error) {
    return { success: false, error: '圖表資料獲取失敗' }
  }
})
