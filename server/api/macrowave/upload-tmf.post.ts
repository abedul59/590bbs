import { promises as fs } from 'fs';
import path from 'path';

export default defineEventHandler(async (event) => {
    // 簡單的密碼驗證，防止外人亂傳資料
    const apiKey = getHeader(event, 'X-Api-Key');
    if (apiKey !== 'macrowave168') {
        return { success: false, message: '授權失敗：無效的 API Key' };
    }

    try {
        const body = await readBody(event);
        
        if (!body || !body.history) {
            return { success: false, message: '上傳格式錯誤，缺乏 history 欄位' };
        }

        // 我們將接收到的資料，存成 tmf_historical_data.json 放在 public 資料夾下
        const filePath = path.join(process.cwd(), 'public', 'tmf_historical_data.json');
        await fs.writeFile(filePath, JSON.stringify(body, null, 2), 'utf-8');

        return { success: true, message: '微台指籌碼資料已成功更新至 Vercel 戰情室！' };

    } catch (error: any) {
        return { success: false, message: '儲存失敗：' + error.message };
    }
});
