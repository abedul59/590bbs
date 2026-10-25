const ENDPOINTS = [
  'https://pyfbsdk59-bengo-scraper-api.hf.space',
  'https://lawxstudents168-bengo-scraper-api.hf.space',
  'https://igveri59-bengo-scraper-api.hf.space'
]

export default defineEventHandler(async (event) => {
  const body = await readBody<{ stock_id?: string }>(event)
  const stockId = String(body?.stock_id || '').trim()
  if (!/^[A-Za-z0-9]{2,12}$/.test(stockId)) {
    throw createError({ statusCode: 400, statusMessage: '股票代碼格式不正確' })
  }

  const callbackUrl = `${getRequestURL(event).origin}/api/bengo/upload`
  let lastError = '所有端點皆無回應'

  for (const endpoint of ENDPOINTS) {
    try {
      await $fetch(`${endpoint}/api/start-scrape`, {
        method: 'POST',
        body: { stock_id: stockId, callback_url: callbackUrl },
        timeout: 60000
      })
      return { success: true, endpoint, callback_url: callbackUrl }
    } catch (error: any) {
      lastError = error?.message || String(error)
    }
  }

  throw createError({ statusCode: 502, statusMessage: `Bengo 雲端爬蟲無法連線：${lastError}` })
})
