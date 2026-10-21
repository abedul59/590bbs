import YahooFinance from 'yahoo-finance2';

const yahooFinance = new YahooFinance();

export default defineEventHandler(async (event) => {
  const query = getQuery(event);
  const ticker = query.ticker as string;
  const range = (query.range as string) || '1y'; 

  if (!ticker) {
    return { error: true, message: '請輸入股票代號 (Ticker symbol is required)' };
  }

  const now = new Date();
  let startDate = new Date();
  
  if (range === '1y') startDate.setFullYear(now.getFullYear() - 1);
  else if (range === '2y') startDate.setFullYear(now.getFullYear() - 2);
  else if (range === '3y') startDate.setFullYear(now.getFullYear() - 3);
  else if (range === '5y') startDate.setFullYear(now.getFullYear() - 5);
  else startDate.setFullYear(now.getFullYear() - 1);

  try {
    const queryOptions = {
      period1: startDate,
      period2: now,
      interval: '1d' as const,
    };
    
    const result = await yahooFinance.chart(ticker, queryOptions);
    
    if (!result.quotes || result.quotes.length === 0) {
        return [];
    }

    const formattedData = result.quotes
      .filter(item => item.close !== null)
      .map((item) => {
        const dateString = item.date.toISOString().split('T')[0];
        return {
          time: dateString,
          open: item.open,
          high: item.high,
          low: item.low,
          close: item.close,
          adjclose: item.adjclose, 
          volume: item.volume || 0 // 🔥 關鍵修復：將成交量一起打包傳給前端
        };
      });

    return formattedData;
    
  } catch (error: any) {
    console.error('Yahoo Finance API 錯誤:', error);
    return {
      error: true,
      message: `抓取失敗 [${error.name || 'Error'}]: ${error.message}`
    };
  }
});
