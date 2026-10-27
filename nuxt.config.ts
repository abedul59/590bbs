export default defineNuxtConfig({
  modules: [
    '@nuxtjs/supabase',
    '@nuxtjs/tailwindcss',
    'dayjs-nuxt'
  ],
  supabase: {
    redirect: false, // 這裡我們使用自訂的動態密碼，不使用 Supabase 預設的 Auth
  },
  runtimeConfig: {
    // Server-only。NUXT_FRED_API_KEY 可在執行階段覆寫此值；舊有
    // FRED_API_KEY 仍由 server/utils/fred.ts 相容讀取。
    fredApiKey: process.env.FRED_API_KEY || process.env.FRED_KEY || '',
    public: {
      shjhsTelegramApiUrl: process.env.NUXT_PUBLIC_SHJHS_TELEGRAM_API_URL || 'https://five90bbs-telegram-shjhs-api.onrender.com',
      macrowaveSyncApiUrls: process.env.NUXT_PUBLIC_MACROWAVE_SYNC_API_URLS || '',
      macrowaveTwstockSyncApiUrl: process.env.NUXT_PUBLIC_MACROWAVE_TWSTOCK_SYNC_API_URL || ''
    }
  },
  dayjs: {
    locales: ['zh-tw'],
    defaultLocale: 'zh-tw',
    defaultTimezone: 'Asia/Taipei',
    plugins: ['timezone', 'utc']
  }
})
