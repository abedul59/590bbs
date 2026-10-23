import YahooFinance from 'yahoo-finance2'

const yahooFinance = new YahooFinance()

export default defineEventHandler(async (event) => {
  setHeader(event, 'Cache-Control', 'public, max-age=3600, s-maxage=21600, stale-while-revalidate=86400')

  try {
    const result = await yahooFinance.chart('0050.TW', {
      period1: new Date('2009-01-01T00:00:00Z'),
      period2: new Date(),
      interval: '1mo'
    })

    const data = (result.quotes || [])
      .filter(quote => quote.close != null)
      .map(quote => ({
        period: quote.date.toISOString().slice(0, 7),
        close: Number(quote.close)
      }))

    if (!data.length) {
      throw new Error('Yahoo Finance 未回傳 0050 月資料')
    }

    return { success: true, data }
  } catch (error: any) {
    console.error('0050 月資料抓取失敗:', error)
    throw createError({
      statusCode: 502,
      statusMessage: `0050 月資料抓取失敗：${error?.message || '未知錯誤'}`
    })
  }
})
