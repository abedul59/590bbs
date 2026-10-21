export default defineEventHandler(async (event) => {
    try {
        const url = `https://query2.finance.yahoo.com/v8/finance/chart/00631L.TW?range=1y&interval=1d`;
        const res = await fetch(url);
        const data = await res.json();
        const result = data.chart.result[0];
        const timestamps = result.timestamp;
        const quote = result.indicators.quote[0];
        
        const history = timestamps.map((t: number, i: number) => ({
            date: new Date(t * 1000).toISOString().split('T')[0],
            open: quote.open[i],
            high: quote.high[i],
            low: quote.low[i],
            close: quote.close[i],
            volume: quote.volume[i] || 0
        })).filter((q: any) => q.close !== null);

        return { success: true, data: history };
    } catch (error: any) {
        return { success: false, message: error.message };
    }
});
