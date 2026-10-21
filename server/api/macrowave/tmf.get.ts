import { promises as fs } from 'fs';
import path from 'path';

export default defineEventHandler(async (event) => {
    try {
        // 直接讀取由本地端上傳的 JSON 檔案
        const filePath = path.join(process.cwd(), 'public', 'tmf_historical_data.json');
        
        const fileContent = await fs.readFile(filePath, 'utf-8');
        const data = JSON.parse(fileContent);
        
        return data; // 直接回傳包含 success, latest, history 的物件

    } catch (error: any) {
        return { 
            success: false, 
            message: '尚未接收到本地端上傳的籌碼資料。請使用本地端同步工具進行第一次更新。' 
        };
    }
});
