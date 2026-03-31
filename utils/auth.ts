import dayjs from 'dayjs'
import utc from 'dayjs/plugin/utc'
import timezone from 'dayjs/plugin/timezone'

dayjs.extend(utc)
dayjs.extend(timezone)

export const getTodayPassword = () => {
  // 強制取得台灣時區的當前時間
  const twTime = dayjs().tz('Asia/Taipei')
  // 格式化為 YYMMDD，例如 2026/03/31 會變成 260331
  return twTime.format('YYMMDD')
}