export default defineEventHandler(async (event) => {
  try {
    // 改寫 fetchYahoo，支援強制傳入起始與結束時間 (period1, period2)
    const fetchYahoo = async (interval: string, range?: string, p1?: number, p2?: number) => {
      let url = `https://query2.finance.yahoo.com/v8/finance/chart/^TWII?interval=${interval}`;
      
      if (p1 !== undefined && p2 !== undefined) {
        url += `&period1=${p1}&period2=${p2}`;
      } else {
        url += `&range=${range}`;
      }
      
      const res = await fetch(url);
      const data = await res.json();
      const result = data.chart.result[0];
      const timestamps = result.timestamp;
      const quote = result.indicators.quote[0];
      
      return timestamps.map((t: number, i: number) => ({
        date: new Date(t * 1000).toISOString().split('T')[0],
        open: quote.open[i],
        high: quote.high[i],
        low: quote.low[i],
        close: quote.close[i],
        volume: quote.volume[i] || 0
      })).filter((q: any) => q.close !== null);
    };

    // 取得目前時間與 1980 年 1 月 1 日的 Unix Timestamp (秒)
    const now = Math.floor(Date.now() / 1000);
    const start1980 = 315532800; 

    // 🔥 核心修正：利用時間戳強迫 Yahoo 吐出真實的 1wk 週線，破解自動降頻的限制
    const [daily, weekly, monthly] = await Promise.all([
      fetchYahoo('1d', '5y'),                            // 日線維持近 5 年，確保載入速度
      fetchYahoo('1wk', undefined, start1980, now),      // 週線強制抓取 1980 至今
      fetchYahoo('1mo', undefined, start1980, now)       // 月線強制抓取 1980 至今
    ]);

    return { success: true, data: { daily, weekly, monthly } };
  } catch (error: any) {
    return { success: false, message: error.message };
  }
});
