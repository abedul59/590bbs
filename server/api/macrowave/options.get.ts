import YahooFinance from 'yahoo-finance2';

const yahooFinance = new YahooFinance();

export default defineEventHandler(async (event) => {
  const query = getQuery(event);
  const ticker = query.ticker as string;
  const dateStr = query.date as string; // 可選的到期日參數

  if (!ticker) {
    return { error: true, message: '請輸入股票代號 (Ticker symbol is required)' };
  }

  try {
    const queryOptions: any = {};
    
    // 如果前端有傳遞特定的到期日，就加入查詢條件中
    if (dateStr) {
      // Yahoo Finance API 可以接受 Date 物件或時間戳
      queryOptions.date = new Date(dateStr);
    }

    // 呼叫 options 方法抓取選擇權鏈
    const result = await yahooFinance.options(ticker, queryOptions);
    
    return result;
    
  } catch (error: any) {
    console.error('Yahoo Finance Options API 錯誤:', error);
    return {
      error: true,
      message: `抓取失敗 [${error.name || 'Error'}]: ${error.message}`
    };
  }
});
