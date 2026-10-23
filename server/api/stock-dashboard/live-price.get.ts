import * as cheerio from 'cheerio';

export default defineEventHandler(async (event) => {
  const { id } = getQuery(event);
  if (!id) return { price: null };

  let price = 0;

  // ==========================================
  // 方案 A：還原原本的聚財網 (wearn.com) 邏輯
  // ==========================================
  try {
    const html = await $fetch<string>(`https://stock.wearn.com/a${id}.html`, {
      headers: {
        // 加上更逼真的瀏覽器偽裝，避免被擋
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Accept-Language': 'zh-TW,zh;q=0.9',
      },
      timeout: 5000 // 5秒超時，避免卡死
    });

    const $ = cheerio.load(html);

    // 尋找成交價
    $('ul').each((i, el) => {
      if ($(el).text().includes('成交價')) {
        const txt = $(el).find('li').first().text().replace(/,/g, '').trim();
        const parsed = parseFloat(txt);
        if (!isNaN(parsed)) price = parsed;
      }
    });

    // 完整還原原本 Python 寫的 fallback 尋找邏輯
    if (price === 0 && $('ul').length > 6) {
      const txt = $('ul').eq(4).find('li').first().text().replace(/,/g, '').trim();
      const parsed = parseFloat(txt);
      if (!isNaN(parsed)) price = parsed;
    }

    // 如果成功抓到大於 0 的數字，直接回傳
    if (price > 0) return { price };

  } catch (error) {
    console.log(`Wearn 抓取失敗 (${id})，切換備用方案...`);
  }

  // ==========================================
  // 方案 B：無敵備用方案 (Yahoo Finance API)
  // ==========================================
  // 由於 Vercel IP 極易被台灣小站封鎖，若上方失敗，自動改用 Yahoo API
  try {
    // 嘗試抓取上市股票 (.TW)
    let yRes = await $fetch<any>(`https://query1.finance.yahoo.com/v8/finance/chart/${id}.TW`);
    let yPrice = yRes?.chart?.result?.[0]?.meta?.regularMarketPrice;

    // 若找不到 (可能是上櫃股票)，改抓上櫃 (.TWO)
    if (!yPrice) {
      yRes = await $fetch<any>(`https://query1.finance.yahoo.com/v8/finance/chart/${id}.TWO`);
      yPrice = yRes?.chart?.result?.[0]?.meta?.regularMarketPrice;
    }

    if (yPrice > 0) return { price: yPrice };
  } catch (error) {
    console.log(`Yahoo API 抓取失敗 (${id})...`);
  }

  // 真的都抓不到才回傳 null
  return { price: null };
});
