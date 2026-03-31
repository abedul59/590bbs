export default defineNuxtConfig({
  modules: [
    '@nuxtjs/supabase',
    '@nuxtjs/tailwindcss',
    'dayjs-nuxt'
  ],
  supabase: {
    redirect: false, // 這裡我們使用自訂的動態密碼，不使用 Supabase 預設的 Auth
  },
  dayjs: {
    locales: ['zh-tw'],
    defaultLocale: 'zh-tw',
    defaultTimezone: 'Asia/Taipei',
    plugins: ['timezone', 'utc']
  }
})