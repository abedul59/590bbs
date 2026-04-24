import dayjs from 'dayjs'
import utc from 'dayjs/plugin/utc'
import timezone from 'dayjs/plugin/timezone'

dayjs.extend(utc)
dayjs.extend(timezone)

export const getTodayPassword = () => {
  // 強制取得台灣時區的當前時間，確保伺服器與本地時間一致
  const twTime = dayjs().tz('Asia/Taipei')
  
  // 格式化為 YYMMDD，並在字尾直接加上 '59'
  // 例如台灣時間 2026/04/24 會變成 '26042459'
  return `${twTime.format('YYMMDD')}59`
}
